##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Types tool export / import

$Id$
"""

from xml.dom.minidom import parseString

import Products
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import INodeExporter
from Products.GenericSetup.interfaces import INodeImporter
from Products.GenericSetup.interfaces import PURGE, UPDATE
from Products.GenericSetup.utils import PrettyDocument

from permissions import ManagePortal
from utils import _xmldir
from utils import ImportConfiguratorBase, ExportConfiguratorBase
from utils import CONVERTER, DEFAULT, KEY

_FILENAME = 'typestool.xml'


def importTypesTool(context):
    """ Import types tool and content types from XML files.
    """
    site = context.getSite()
    mode = context.shouldPurge() and PURGE or UPDATE
    ttool = getToolByName(site, 'portal_types')

    if context.shouldPurge():
        for type in ttool.objectIds():
            ttool._delObject(type)

    ttc = TypesToolImportConfigurator(site)
    xml = context.readDataFile(_FILENAME)
    if xml is None:
        return 'Types tool: Nothing to import.'

    tool_info = ttc.parseXML(xml)

    for type_info in tool_info['types']:

        filename = type_info['filename']
        sep = filename.rfind('/')
        if sep == -1:
            body = context.readDataFile( filename )
        else:
            body = context.readDataFile( filename[sep+1:], filename[:sep] )

        if body is None:
            continue

        root = parseString(body).documentElement
        ti_id = str(root.getAttribute('name'))
        if not ti_id:
            # BBB: for CMF 1.5 profiles
            #      ID moved from 'id' to 'name'.
            ti_id = str(root.getAttribute('id'))
        if ti_id not in ttool.objectIds():
            # BBB: for CMF 1.5 profiles
            #     'kind' is now 'meta_type', the old 'meta_type' attribute
            #      was replaced by a property element.
            meta_type = str(root.getAttribute('kind'))
            if not meta_type:
                meta_type = str(root.getAttribute('meta_type'))
            for mt_info in Products.meta_types:
                if mt_info['name'] == meta_type:
                    ttool._setObject(ti_id, mt_info['instance'](ti_id))
                    break
            else:
                raise ValueError('unknown meta_type \'%s\'' % ti_id)

        ti = ttool.getTypeInfo(ti_id)
        importer = INodeImporter(ti, None)
        if importer is None:
            continue

        importer.importNode(root, mode=mode)

    # XXX: YAGNI?
    # importScriptsToContainer(ttool, ('typestool_scripts',),
    #                          context)

    return 'Types tool imported.'

def exportTypesTool(context):
    """ Export types tool content types as a set of XML files.
    """
    site = context.getSite()

    ttool = getToolByName(site, 'portal_types')
    if ttool is None:
        return 'Types tool: Nothing to export.'

    ttc = TypesToolExportConfigurator(site).__of__(site)
    tool_xml = ttc.generateXML()
    context.writeDataFile(_FILENAME, tool_xml, 'text/xml')

    for ti_id in ttool.listContentTypes():
        type_filename = '%s.xml' % ti_id.replace( ' ', '_' )
        ti = getattr(ttool, ti_id)

        exporter = INodeExporter(ti)
        if exporter is None:
            continue

        doc = PrettyDocument()
        doc.appendChild(exporter.exportNode(doc))
        context.writeDataFile(type_filename, doc.toprettyxml(' '), 'text/xml',
                              'types')

    # XXX: YAGNI?
    # exportScriptsFromContainer(ttool, ('typestool_scripts',))

    return 'Types tool exported'


class TypesToolImportConfigurator(ImportConfiguratorBase):

    def _getImportMapping(self):

        return {
          'types-tool':
            { 'type':     {KEY: 'types', DEFAULT: (),
                           CONVERTER: self._convertTypes} },
          'type':
            { 'id':       {},
              'filename': {DEFAULT: '%(id)s'} } }

    def _convertTypes(self, val):

        for type in val:
            if type['filename'] == type['id']:
                type['filename'] = _getTypeFilename( type['filename'] )

        return val

InitializeClass(TypesToolImportConfigurator)


class TypesToolExportConfigurator(ExportConfiguratorBase):

    security = ClassSecurityInfo()

    security.declareProtected( ManagePortal, 'listTypeInfo' )
    def listTypeInfo( self ):

        """ Return a list of mappings for each type info in the site.

        o These mappings are pretty much equivalent to the stock
          'factory_type_information' elements used everywhere in the
          CMF.
        """
        result = []
        typestool = getToolByName( self._site, 'portal_types' )

        type_ids = typestool.listContentTypes()

        for type_id in type_ids:
            info = {'id': type_id}

            if ' ' in type_id:
                info['filename'] = _getTypeFilename(type_id)

            result.append(info)

        return result

    def _getExportTemplate(self):

        return PageTemplateFile('ticToolExport.xml', _xmldir)

InitializeClass(TypesToolExportConfigurator)


def _getTypeFilename( type_id ):

    """ Return the name of the file which holds info for a given type.
    """
    return 'types/%s.xml' % type_id.replace( ' ', '_' )
