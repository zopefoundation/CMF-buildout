#!/usr/bin/env python2.4
##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Program to extract internationalization markup from Python Code,
Page Templates and ZCML.

This tool will extract all findable message strings from all
internationalizable files in your Zope 3 product. It only extracts message ids
of the specified domain. It defaults to the 'zope' domain and the zope
package.

Note: The Python Code extraction tool does not support domain
      registration, so that all message strings are returned for
      Python code.

Note: The script expects to be executed either from inside the Zope 3 source
      tree or with the Zope 3 source tree on the Python path.  Execution from
      a symlinked directory inside the Zope 3 source tree will not work.

Usage: i18nextract.py [options]
Options:
    -h / --help
        Print this message and exit.
    -d / --domain <domain>
        Specifies the domain that is supposed to be extracted (i.e. 'zope')
    -p / --path <path>
        Specifies the package that is supposed to be searched
        (i.e. 'zope/app')
    -o dir
        Specifies a directory, relative to the package in which to put the
        output translation template.
    -x dir
        Specifies a directory, relative to the package, to exclude.
        May be used more than once.

$Id$
"""
# XXX: This is a modified copy of zope3's utilities/i18nextract.py (r41131).
#      It includes some modified code from zope.app.locales.extract (r41131).
#      Extracting from ZCML is disabled for now.
#
#      This is just used to create .pot files for CMF. Don't make your code
#      depend on it, it might be changed or removed without further notice!

import fnmatch
import time
import tokenize
import traceback

from zope.app.locales.extract import POTMaker, TokenEater
from zope.app.locales.pygettext import safe_eval, normalize, make_escapes


DEFAULT_CHARSET = 'UTF-8'
DEFAULT_ENCODING = '8bit'

pot_header = '''\
##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
msgid ""
msgstr ""
"Project-Id-Version: CMF 2.0\\n"
"POT-Creation-Date: $Date$\\n"
"Language-Team: CMF Developers <zope-cmf@zope.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=%(charset)s\\n"
"Content-Transfer-Encoding: %(encoding)s\\n"

'''

class POTMaker(POTMaker):
    """This class inserts sets of strings into a POT file.
    """

    def write(self):
        file = open(self._output_filename, 'w')
        file.write(pot_header % {'time':     time.ctime(),
                                 'version':  self._getProductVersion(),
                                 'charset':  DEFAULT_CHARSET,
                                 'encoding': DEFAULT_ENCODING})

        # Sort the catalog entries by filename
        catalog = self.catalog.values()
        catalog.sort()

        # Write each entry to the file
        for entry in catalog:
            entry.write(file)

        file.close()

def find_files(dir, pattern, exclude=()):
    files = []

    def visit(files, dirname, names):
        names[:] = filter(lambda x:x not in exclude, names)
        files += [os.path.join(dirname, name)
                  for name in fnmatch.filter(names, pattern)
                  if name not in exclude]

    os.path.walk(dir, visit, files)
    return files

def py_strings(dir, domain="zope", exclude=()):
    """Retrieve all Python messages from `dir` that are in the `domain`.
    """
    eater = TokenEater()
    make_escapes(0)
    for filename in find_files(
            dir, '*.py', exclude=('extract.py', 'pygettext.py')+tuple(exclude)):
        fp = open(filename)
        try:
            eater.set_filename(filename)
            try:
                tokenize.tokenize(fp.readline, eater)
            except tokenize.TokenError, e:
                print >> sys.stderr, '%s: %s, line %d, column %d' % (
                    e[0], filename, e[1][0], e[1][1])
        finally:
            fp.close()
    # One limitation of the Python message extractor is that it cannot
    # determine the domain of the string, since it is not contained anywhere
    # directly. The only way this could be done is by loading the module and
    # inspect the '_' function. For now we simply assume that all the found
    # strings have the domain the user specified.
    return eater.getCatalog()

def zcml_strings(dir, domain="zope", site_zcml=None):
    """Retrieve all ZCML messages from `dir` that are in the `domain`.
    """
    return {}

def tal_strings(dir, domain="zope", include_default_domain=False, exclude=()):
    """Retrieve all TAL messages from `dir` that are in the `domain`.
    """
    # We import zope.tal.talgettext here because we can't rely on the
    # right sys path until app_dir has run
    from zope.pagetemplate.pagetemplatefile import sniff_type
    from zope.pagetemplate.pagetemplatefile import XML_PREFIX_MAX_LENGTH
    from zope.tal.talgettext import POEngine, POTALInterpreter
    from zope.tal.htmltalparser import HTMLTALParser
    from zope.tal.talparser import TALParser
    engine = POEngine()

    class Devnull(object):
        def write(self, s):
            pass

    filenames = find_files(dir, '*.pt', exclude=tuple(exclude)) \
              + find_files(dir, '*.html', exclude=tuple(exclude)) \
              + find_files(dir, '*.xml', exclude=tuple(exclude))

    for filename in sorted(filenames):
        # This is taken from zope/pagetemplate/pagetemplatefile.py (r40504)
        f = open(filename, "rb")
        try:
            text = f.read(XML_PREFIX_MAX_LENGTH)
        except:
            f.close()
            raise
        type_ = sniff_type(text)
        if type_ == "text/xml":
            text += f.read()
        else:
            # For HTML, we really want the file read in text mode:
            f.close()
            f = open(filename)
            text = f.read()
        f.close()

        try:
            engine.file = filename
            if type_ != "text/xml":
                p = HTMLTALParser()
            else:
                p = TALParser()
            p.parseString(text)
            program, macros = p.getCode()
            POTALInterpreter(program, macros, engine, stream=Devnull(),
                             metal=False)()
        except: # Hee hee, I love bare excepts!
            print 'There was an error processing', filename
            traceback.print_exc()

    # See whether anything in the domain was found
    if not engine.catalog.has_key(domain):
        return {}
    # We do not want column numbers.
    catalog = engine.catalog[domain].copy()
    # When the Domain is 'default', then this means that none was found;
    # Include these strings; yes or no?
    if include_default_domain:
        catalog.update(engine.catalog['zope'])
    for msgid, locations in catalog.items():
        catalog[msgid] = map(lambda l: (l[0], l[1][0]), locations)
    return catalog


import os, sys, getopt

def usage(code, msg=''):
    # Python 2.1 required
    print >> sys.stderr, __doc__
    if msg:
        print >> sys.stderr, msg
    sys.exit(code)

def app_dir():
    try:
        import zope
    except ImportError:
        # Couldn't import zope, need to add something to the Python path

        # Get the path of the src
        path = os.path.abspath(os.getcwd())
        while not path.endswith('src'):
            parentdir = os.path.dirname(path)
            if path == parentdir:
                # root directory reached
                break
            path = parentdir
        sys.path.insert(0, path)

        try:
            import zope
        except ImportError:
            usage(1, "Make sure the script has been executed "
                     "inside Zope 3 source tree.")

    return os.path.dirname(zope.__file__)

def main(argv=sys.argv):
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'hd:p:o:x:',
            ['help', 'domain=', 'path=', 'python-only'])
    except getopt.error, msg:
        usage(1, msg)

    domain = 'zope'
    path = app_dir()
    include_default_domain = True
    output_dir = None
    exclude_dirs = []
    python_only = None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-d', '--domain'):
            domain = arg
            include_default_domain = False
        elif opt in ('-o', ):
            output_dir = arg
        elif opt in ('-x', ):
            exclude_dirs.append(arg)
        elif opt in ('--python-only',):
            python_only = True
        elif opt in ('-p', '--path'):
            if not os.path.exists(arg):
                usage(1, 'The specified path does not exist.')
            path = arg
            # We might not have an absolute path passed in.
            if not path == os.path.abspath(path):
                cwd = os.getcwd()
                # This is for symlinks. Thanks to Fred for this trick.
                if os.environ.has_key('PWD'):
                    cwd = os.environ['PWD']
                path = os.path.normpath(os.path.join(cwd, arg))

    # When generating the comments, we will not need the base directory info,
    # since it is specific to everyone's installation
    base_dir = path+os.sep

    output_file = domain+'.pot'
    if output_dir:
        output_dir = os.path.join(path, output_dir)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_file = os.path.join(output_dir, output_file)

    print "base path: %r\n" \
          "search path: %s\n" \
          "exclude dirs: %r\n" \
          "domain: %r\n" \
          "output file: %r" \
          % (base_dir, path, exclude_dirs, domain, output_file)

    maker = POTMaker(output_file, path)
    maker.add(py_strings(path, domain, exclude=exclude_dirs), base_dir)
    if not python_only:
        maker.add(zcml_strings(path, domain), base_dir)
        maker.add(tal_strings(path, domain, include_default_domain,
                              exclude=exclude_dirs), base_dir)
    maker.write()

    manual_file = os.path.join(output_dir, domain+'-manual.pot')
    if os.path.exists(manual_file):
        manual = file(manual_file, 'r')
        auto = file(output_file, 'a')
        auto.write(manual.read())
        auto.close()
        manual.close()

if __name__ == '__main__':
    main()
