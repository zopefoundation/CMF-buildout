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
"""Cookie crumbler setup handlers.

$Id$
"""

from xml.dom.minidom import parseString

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import INodeExporter
from Products.GenericSetup.interfaces import INodeImporter
from Products.GenericSetup.interfaces import PURGE, UPDATE
from Products.GenericSetup.utils import PrettyDocument

_FILENAME = 'cookieauth.xml'


def importCookieCrumbler(context):
    """ Import cookie crumbler settings from an XML file.
    """
    site = context.getSite()
    mode = context.shouldPurge() and PURGE or UPDATE
    cctool = getToolByName(site, 'cookie_authentication')

    body = context.readDataFile(_FILENAME)
    if body is None:
        return 'Cookie crumbler: Nothing to import.'

    importer = INodeImporter(cctool, None)
    if importer is None:
        return 'Cookie crumbler: Import adapter misssing.'

    importer.importNode(parseString(body).documentElement, mode=mode)
    return 'Cookie crumbler settings imported.'

def exportCookieCrumbler(context):
    """ Export cookie crumbler settings as an XML file.
    """
    site = context.getSite()

    cctool = getToolByName(site, 'cookie_authentication', None)
    if cctool is None:
        return 'Cookie crumbler: Nothing to export.'

    exporter = INodeExporter(cctool)
    if exporter is None:
        return 'Cookie crumbler: Export adapter misssing.'

    doc = PrettyDocument()
    doc.appendChild(exporter.exportNode(doc))
    context.writeDataFile(_FILENAME, doc.toprettyxml(' '), 'text/xml')
    return 'Cookie crumbler settings exported.'
