##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Filesystem exporter / importer adapters.

$Id$
"""

from csv import reader
from csv import register_dialect
from csv import writer
from ConfigParser import ConfigParser
import re
from StringIO import StringIO

from zope.interface import implements
from zope.interface import directlyProvides

from Products.CMFCore.interfaces import IFilesystemExporter
from Products.CMFCore.interfaces import IFilesystemImporter
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

#
#   setup_tool handlers
#
def exportSiteStructure(context):
    IFilesystemExporter(context.getSite()).export(context, 'structure')

def importSiteStructure(context):
    IFilesystemImporter(context.getSite()).import_(context, 'structure')


#
#   Filesystem export/import adapters
#
class StructureFolderWalkingAdapter(object):
    """ Tree-walking exporter for "folderish" types.

    Folderish instances are mapped to directories within the 'structure'
    portion of the profile, where the folder's relative path within the site
    corresponds to the path of its directory under 'structure'.

    The subobjects of a folderish instance are enumerated in the '.objects'
    file in the corresponding directory.  This file is a CSV file, with one
    row per subobject, with the following wtructure::

     "<subobject id>","<subobject portal_type>"

    Subobjects themselves are represented as individual files or
    subdirectories within the parent's directory.
    """

    implements(IFilesystemExporter, IFilesystemImporter)

    def __init__(self, context):
        self.context = context

    def export(self, export_context, subdir):
        """ See IFilesystemExporter.
        """
        # Enumerate exportable children
        exportable = self.context.contentItems()
        exportable = [x + (IFilesystemExporter(x, None),) for x in exportable]
        exportable = [x for x in exportable if x[1] is not None]

        stream = StringIO()
        csv_writer = writer(stream)

        for object_id, object, ignored in exportable:
            csv_writer.writerow((object_id, object.getPortalTypeName()))

        if not ISiteRoot.providedBy(self.context):
            subdir = '%s/%s' % (subdir, self.context.getId())

        export_context.writeDataFile('.objects',
                                     text=stream.getvalue(),
                                     content_type='text/comma-separated-values',
                                     subdir=subdir,
                                    )

        parser = ConfigParser()

        parser.set('DEFAULT', 'Title', self.context.Title())
        parser.set('DEFAULT', 'Description', self.context.Description())
        stream = StringIO()
        parser.write(stream)

        export_context.writeDataFile('.properties',
                                    text=stream.getvalue(),
                                    content_type='text/plain',
                                    subdir=subdir,
                                    )

        for id, object in self.context.objectItems():

            adapter = IFilesystemExporter(object, None)

            if adapter is not None:
                adapter.export(export_context, subdir)

    def import_(self, import_context, subdir):
        """ See IFilesystemImporter.
        """
        context = self.context
        if not ISiteRoot.providedBy(context):
            subdir = '%s/%s' % (subdir, context.getId())

        preserve = import_context.readDataFile('.preserve', subdir)

        prior = context.contentIds()

        if not preserve:
            preserve = []
        else:
            preserve = _globtest(preserve, prior)

        for id in prior:
            if id not in preserve:
                context._delObject(id)

        objects = import_context.readDataFile('.objects', subdir)
        if objects is None:
            return

        dialect = 'excel'
        stream = StringIO(objects)

        rowiter = reader(stream, dialect)

        existing = context.objectIds()

        for object_id, portal_type in rowiter:

            if object_id not in existing:
                object = self._makeInstance(object_id, portal_type,
                                            subdir, import_context)
                if object is None:
                    message = "Couldn't make instance: %s/%s" % (subdir,
                                                                 object_id)
                    import_context.note('SFWA', message)
                    continue

            wrapped = context._getOb(object_id)

            IFilesystemImporter(wrapped).import_(import_context, subdir)

    def _makeInstance(self, id, portal_type, subdir, import_context):

        context = self.context
        properties = import_context.readDataFile('.properties',
                                                 '%s/%s' % (subdir, id))
        tool = getToolByName(context, 'portal_types')

        try:
            tool.constructContent(portal_type, context, id)
        except ValueError: # invalid type
            return None

        content = context._getOb(id)

        if properties is not None:
            lines = properties.splitlines()

            stream = StringIO('\n'.join(lines))
            parser = ConfigParser(defaults={'title': '', 'description': 'NONE'})
            parser.readfp(stream)

            title = parser.get('DEFAULT', 'title')
            description = parser.get('DEFAULT', 'description')

            content.setTitle(title)
            content.setDescription(description)

        return content


def _globtest(globpattern, namelist):
    """ Filter names in 'namelist', returning those which match 'globpattern'.
    """
    import re
    pattern = globpattern.replace(".", r"\.")       # mask dots
    pattern = pattern.replace("*", r".*")           # change glob sequence
    pattern = pattern.replace("?", r".")            # change glob char
    pattern = '|'.join(pattern.split())             # 'or' each line

    compiled = re.compile(pattern)

    return filter(compiled.match, namelist)


class CSVAwareFileAdapter(object):
    """ Adapter for content whose "natural" representation is CSV.
    """
    implements(IFilesystemExporter, IFilesystemImporter)

    def __init__(self, context):
        self.context = context

    def export(self, export_context, subdir):
        """ See IFilesystemExporter.
        """
        export_context.writeDataFile('%s.csv' % self.context.getId(),
                                     self.context.as_csv(),
                                     'text/comma-separated-values',
                                     subdir,
                                    )

    def listExportableItems(self):
        """ See IFilesystemExporter.
        """
        return ()

    def import_(self, import_context, subdir):
        """ See IFilesystemImporter.
        """
        cid = self.context.getId()
        data = import_context.readDataFile('%s.csv' % cid, subdir)
        if data is None:
            import_context.note('CSAFA',
                                'no .csv file for %s/%s' % (subdir, cid))
        else:
            stream = StringIO(data)
            self.context.put_csv(stream)

class INIAwareFileAdapter(object):
    """ Exporter/importer for content whose "natural" representation is CSV.
    """
    implements(IFilesystemExporter, IFilesystemImporter)

    def __init__(self, context):
        self.context = context

    def export(self, export_context, subdir):
        """ See IFilesystemExporter.
        """
        export_context.writeDataFile('%s.ini' % self.context.getId(),
                                     self.context.as_ini(),
                                     'text/plain',
                                     subdir,
                                    )

    def listExportableItems(self):
        """ See IFilesystemExporter.
        """
        return ()

    def import_(self, import_context, subdir):
        """ See IFilesystemImporter.
        """
        cid = self.context.getId()
        data = import_context.readDataFile('%s.ini' % cid, subdir)
        if data is None:
            import_context.note('SGAIFA',
                                'no .ini file for %s/%s' % (subdir, cid))
        else:
            self.context.put_ini(data)


class FauxDAVRequest:

    def __init__(self, **kw):
        self._data = {}
        self._headers = {}
        self._data.update(kw)

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def get_header(self, key, default=None):
        return self._headers.get(key, default)

class FauxDAVResponse:
    def setHeader(self, key, value, lock=False):
        pass  # stub this out to mollify webdav.Resource
    def setStatus(self, value, reason=None):
        pass  # stub this out to mollify webdav.Resource

class DAVAwareFileAdapter(object):
    """ Exporter/importer for content who handle their own FTP / DAV PUTs.
    """
    implements(IFilesystemExporter, IFilesystemImporter)

    def __init__(self, context):
        self.context = context

    def export(self, export_context, subdir):
        """ See IFilesystemExporter.
        """
        export_context.writeDataFile('%s' % self.context.getId(),
                                     self.context.manage_FTPget(),
                                     'text/plain',
                                     subdir,
                                    )

    def listExportableItems(self):
        """ See IFilesystemExporter.
        """
        return ()

    def import_(self, import_context, subdir):
        """ See IFilesystemImporter.
        """
        cid = self.context.getId()
        data = import_context.readDataFile('%s' % cid, subdir)
        if data is None:
            import_context.note('SGAIFA',
                                'no .ini file for %s/%s' % (subdir, cid))
        else:
            request = FauxDAVRequest(BODY=data, BODYFILE=data)
            response = FauxDAVResponse()
            self.context.PUT(request, response)
