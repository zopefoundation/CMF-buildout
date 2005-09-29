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
"""Catalog tool setup handlers.

$Id$
"""

from xml.dom.minidom import parseString

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import INodeExporter
from Products.GenericSetup.interfaces import INodeImporter
from Products.GenericSetup.interfaces import PURGE, UPDATE
from Products.GenericSetup.utils import PrettyDocument

_FILENAME = 'catalog.xml'


def importCatalogTool(context):
    """ Import catalog tool.
    """
    site = context.getSite()
    mode = context.shouldPurge() and PURGE or UPDATE
    ctool = getToolByName(site, 'portal_catalog')

    body = context.readDataFile(_FILENAME)
    if body is None:
        return 'Catalog tool: Nothing to import.'

    importer = INodeImporter(ctool, None)
    if importer is None:
        return 'Catalog tool: Import adapter misssing.'

    importer.importNode(parseString(body).documentElement, mode=mode)
    return 'Catalog tool imported.'

def exportCatalogTool(context):
    """ Export catalog tool.
    """
    site = context.getSite()

    ctool = getToolByName(site, 'portal_catalog', None)
    if ctool is None:
        return 'Catalog tool: Nothing to export.'

    exporter = INodeExporter(ctool)
    if exporter is None:
        return 'Catalog tool: Export adapter misssing.'

    doc = PrettyDocument()
    doc.appendChild(exporter.exportNode(doc))
    context.writeDataFile(_FILENAME, doc.toprettyxml(' '), 'text/xml')
    return 'Catalog tool exported.'
