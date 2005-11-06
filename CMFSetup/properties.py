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
"""Site properties setup handlers.

$Id$
"""

from xml.dom.minidom import parseString

from Products.GenericSetup.interfaces import INodeExporter
from Products.GenericSetup.interfaces import INodeImporter
from Products.GenericSetup.interfaces import PURGE, UPDATE
from Products.GenericSetup.utils import PrettyDocument

_FILENAME = 'properties.xml'


def importSiteProperties(context):
    """ Import site properties from an XML file.
    """
    site = context.getSite()
    mode = context.shouldPurge() and PURGE or UPDATE

    body = context.readDataFile(_FILENAME)
    if body is None:
        return 'Site properties: Nothing to import.'

    importer = INodeImporter(site, None)
    if importer is None:
        return 'Site properties: Import adapter misssing.'

    importer.importNode(parseString(body).documentElement, mode=mode)
    return 'Site properties imported.'

def exportSiteProperties(context):
    """ Export site properties as an XML file.
    """
    site = context.getSite()

    exporter = INodeExporter(site)
    if exporter is None:
        return 'Site properties: Export adapter misssing.'

    doc = PrettyDocument()
    doc.appendChild(exporter.exportNode(doc))
    context.writeDataFile(_FILENAME, doc.toprettyxml(' '), 'text/xml')
    return 'Site properties exported.'
