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
"""ContentTypeRegistry setup handlers.

$Id$
"""

from xml.dom.minidom import parseString

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import INodeExporter
from Products.GenericSetup.interfaces import INodeImporter
from Products.GenericSetup.interfaces import PURGE, UPDATE
from Products.GenericSetup.utils import PrettyDocument

_FILENAME = 'contenttyperegistry.xml'


def importContentTypeRegistry(context):
    """ Import content type registry settings from an XML file.
    """
    site = context.getSite()
    mode = context.shouldPurge() and PURGE or UPDATE
    ctr = getToolByName(site, 'content_type_registry', None)

    body = context.readDataFile(_FILENAME)
    if body is None:
        return 'Content type registry: Nothing to import.'

    importer = INodeImporter(ctr, None)
    if importer is None:
        return 'Content type registry: Import adapter misssing.'

    importer.importNode(parseString(body).documentElement, mode=mode)
    return 'Content type registry settings imported.'

def exportContentTypeRegistry(context):
    """ Export content type registry settings as an XML file.
    """
    site = context.getSite()

    ctr = getToolByName(site, 'content_type_registry', None)
    if ctr is None:
        return 'Content type registry: Nothing to export.'

    exporter = INodeExporter(ctr)
    if exporter is None:
        return 'Content type registry: Export adapter misssing.'

    doc = PrettyDocument()
    doc.appendChild(exporter.exportNode(doc))
    context.writeDataFile(_FILENAME, doc.toprettyxml(' '), 'text/xml')
    return 'Content type registry settings exported.'
