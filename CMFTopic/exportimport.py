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
""" GenericSetup export / import support for topics / criteria.

$Id$
"""
from xml.dom.minidom import parseString

from Acquisition import Implicit
from zope.interface import implements

from Products.GenericSetup.interfaces import IFilesystemExporter
from Products.GenericSetup.interfaces import IFilesystemImporter
from Products.GenericSetup.content import FolderishExporterImporter

try:
    from Products.GenericSetup.utils import PageTemplateResource
except ImportError: # BBB:  no egg support
    from Products.PageTemplates.PageTemplateFile \
        import PageTemplateFile as PageTemplateResource


class TopicExportImport(FolderishExporterImporter):
    """ Dump topic criteria to / from an XML file.
    """
    implements(IFilesystemExporter, IFilesystemImporter)

    encoding = None
    _FILENAME = 'criteria.xml'
    _ROOT_TAGNAME = 'criteria'

    def __init__(self, context):
        self.context = context

    def listExportableItems(self):
        """ See IFilesystemExporter.
        """
        criteria_metatypes = self.context._criteria_metatype_ids()
        return [x for x in FolderishExporterImporter.listExportableItems(self)
                   if x[1].meta_type not in criteria_metatypes]

    def export(self, export_context, subdir, root=False):
        """ See IFilesystemExporter.
        """
        FolderishExporterImporter.export(self, export_context, subdir, root)
        template = PageTemplateResource('xml/%s' % self._FILENAME,
                                        globals()).__of__(self.context)
        export_context.writeDataFile('%s/criteria.xml' % self.context.getId(),
                                     template(info=self._getExportInfo()),
                                     'text/xml',
                                     subdir,
                                    )

    def import_(self, import_context, subdir, root=False):
        """ See IFilesystemImporter
        """
        return
        FolderishExporterImporter.import_(self, import_context, subdir, root)

        self.encoding = import_context.getEncoding()

        if import_context.shouldPurge():
            self._purgeContext()

        data = import_context.readDataFile('%s/criteria.xml'
                                                % self.context.getId(),
                                           subdir)

        if data is not None:

            dom = parseString(data)
            root = dom.firstChild
            assert root.tagName == self._ROOT_TAGNAME

            self.context.title = self._getNodeAttr(root, 'title', None)
            self._updateFromDOM(root)

    def _getNodeAttr(self, node, attrname, default=None):
        attr = node.attributes.get(attrname)
        if attr is None:
            return default
        value = attr.value
        if isinstance(value, unicode) and self.encoding is not None:
            value = value.encode(self.encoding)
        return value

    def _purgeContext(self):
        return
        context = self.context
        criterion_ids = context.objectIds(context._criteria_metatype_ids())
        for criterion_id in criterion_ids:
            self.context._delObject(criterion_id)

    def _updateFromDOM(self, root):
        return
        for group in root.getElementsByTagName('group'):
            group_id = self._getNodeAttr(group, 'group_id', None)
            predicate = self._getNodeAttr(group, 'predicate', None)
            title = self._getNodeAttr(group, 'title', None)
            description = self._getNodeAttr(group, 'description', None)
            active = self._getNodeAttr(group, 'active', None)

            self.context.addGroup(group_id,
                                  predicate,
                                  title,
                                  description,
                                  active == 'True',
                                 )
    def _getExportInfo(self):
        context = self.context
        criterion_info = []

        for criterion_id, criterion in context.objectItems(
                                        context._criteria_metatype_ids()):

            # SortCriterion stashes the 'field' as 'index'.
            field = getattr(criterion, 'index', criterion.field)

            info = {'criterion_id': criterion_id,
                    'type': criterion.meta_type,
                    'field': field,
                    'attributes': []
                   }

            attributes = info['attributes']
            for attrname in criterion.editableAttributes():
                value = getattr(criterion, attrname)
                if type(value) in (tuple, list):
                    value = ','.join(value)
                attributes.append((attrname, value))

            criterion_info.append(info)

        return {'criteria': criterion_info,
               }

