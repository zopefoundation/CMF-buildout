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
"""Extract message strings from python modules, page template files
and ZCML files.

$Id$
"""
# XXX: This is a modified copy of zope.app.locales.extract (r79598).
#      Extracting from ZCML is disabled for now.
#
#      This is just used to create .pot files for CMF. Don't make your code
#      depend on it, it might be changed or removed without further notice!
__docformat__ = 'restructuredtext'

import os, sys, fnmatch
import getopt
import time
import traceback

from zope.app.locales.extract import DEFAULT_CHARSET
from zope.app.locales.extract import DEFAULT_ENCODING
from zope.app.locales.extract import find_files
from zope.app.locales.extract import normalize_path
from zope.app.locales.extract import POTMaker
from zope.app.locales.extract import py_strings
from zope.app.locales.extract import zcml_strings
from zope.app.locales.extract import usage

pot_header = '''\
##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors. All Rights Reserved.
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
"Project-Id-Version: CMF 2.2\\n"
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
                                 'charset':  DEFAULT_CHARSET,
                                 'encoding': DEFAULT_ENCODING})

        # Sort the catalog entries by filename
        catalog = self.catalog.values()
        catalog.sort()

        # Write each entry to the file
        for entry in catalog:
            entry.write(file)

        file.close()


def tal_strings(dir, domain="zope", include_default_domain=False, exclude=()):
    """Retrieve all TAL messages from `dir` that are in the `domain`.

      >>> from zope.app.locales import extract
      >>> import tempfile
      >>> dir = tempfile.mkdtemp()
      
    Let's create a page template in the i18n domain ``test``:
      >>> testpt = open(os.path.join(dir, 'test.pt'), 'w')
      >>> testpt.write('<tal:block i18n:domain="test" i18n:translate="">test</tal:block>')
      >>> testpt.close()
      
    And now one in no domain:
      >>> nopt = open(os.path.join(dir, 'no.pt'), 'w')
      >>> nopt.write('<tal:block i18n:translate="">no domain</tal:block>')
      >>> nopt.close()

    Now let's find the strings for the domain ``test``:

      >>> extract.tal_strings(dir, domain='test', include_default_domain=True)
      {'test': [('...test.pt', 1)], 'no domain': [('...no.pt', 1)]}

    And now an xml file
      >>> xml = open(os.path.join(dir, 'xml.pt'), 'w')
      >>> xml.write('''<?xml version="1.0" encoding="utf-8"?>
      ... <rss version="2.0"
      ...     i18n:domain="xml"
      ...     xmlns:i18n="http://xml.zope.org/namespaces/i18n"
      ...     xmlns:tal="http://xml.zope.org/namespaces/tal"
      ...     xmlns="http://purl.org/rss/1.0/modules/content/">
      ...  <channel>
      ...    <link i18n:translate="">Link Content</link>
      ...  </channel>
      ... </rss>
      ... ''')
      >>> xml.close()
      >>> extract.tal_strings(dir, domain='xml')
      {u'Link Content': [('...xml.pt', 8)]}

    Cleanup

      >>> import shutil
      >>> shutil.rmtree(dir) 
    """

    # We import zope.tal.talgettext here because we can't rely on the
    # right sys path until app_dir has run
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
        f = file(filename,'rb')
        start = f.read(6)
        f.close()
        if start.startswith('<?xml'):
            parserFactory = TALParser
        else:
            parserFactory = HTMLTALParser
        try:
            engine.file = filename
            p = parserFactory()
            p.parseFile(filename)
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
        defaultCatalog = engine.catalog.get('default')
        if defaultCatalog == None:
            engine.catalog['default'] = {}
        catalog.update(engine.catalog['default'])
    for msgid, locations in catalog.items():
        catalog[msgid] = map(lambda l: (l[0], l[1][0]), locations)
    return catalog

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(
            argv,
            'hd:s:i:p:o:x:',
            ['help', 'domain=', 'site_zcml=', 'path=', 'python-only'])
    except getopt.error, msg:
        usage(1, msg)

    domain = 'zope'
    path = None
    include_default_domain = True
    output_dir = None
    exclude_dirs = []
    python_only = False
    site_zcml = None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-d', '--domain'):
            domain = arg
        elif opt in ('-s', '--site_zcml'):
            if not os.path.exists(arg):
                usage(1, 'The specified location for site.zcml does not exist')
            site_zcml = normalize_path(arg)
        elif opt in ('-e', '--exclude-default-domain'):
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
            path = normalize_path(arg)

    if path is None:
        usage(1, 'You need to provide the module search path with -p PATH.')
    sys.path.insert(0, path)

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
          "'site.zcml' location: %s\n" \
          "exclude dirs: %r\n" \
          "domain: %r\n" \
          "include default domain: %r\n" \
          "output file: %r\n" \
          "Python only: %r" \
          % (base_dir, path, site_zcml, exclude_dirs, domain,
             include_default_domain, output_file, python_only)

    maker = POTMaker(output_file, path)
    maker.add(py_strings(path, domain, exclude=exclude_dirs), base_dir)
    if not python_only:
        if site_zcml is not None:
            maker.add(zcml_strings(path, domain, site_zcml), base_dir)
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
