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
"""Actions tool setup handlers.

$Id$
"""

from xml.dom.minidom import parseString

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import INodeExporter
from Products.GenericSetup.interfaces import INodeImporter
from Products.GenericSetup.interfaces import PURGE, UPDATE
from Products.GenericSetup.utils import PrettyDocument

_FILENAME = 'actions.xml'


def importActionProviders(context):
    """ Import actions tool.
    """
    site = context.getSite()
    mode = context.shouldPurge() and PURGE or UPDATE
    atool = getToolByName(site, 'portal_actions')

    body = context.readDataFile(_FILENAME)
    if body is None:
        return 'Actions tool: Nothing to import.'

    importer = INodeImporter(atool, None)
    if importer is None:
        return 'Actions tool: Import adapter misssing.'

    importer.importNode(parseString(body).documentElement, mode=mode)
    return 'Actions tool imported.'

def exportActionProviders(context):
    """ Export actions tool.
    """
    site = context.getSite()

    atool = getToolByName(site, 'portal_actions', None)
    if atool is None:
        return 'Actions tool: Nothing to export.'

    exporter = INodeExporter(atool)
    if exporter is None:
        return 'Actions tool: Export adapter misssing.'

    doc = PrettyDocument()
    doc.appendChild(exporter.exportNode(doc))
    context.writeDataFile(_FILENAME, doc.toprettyxml(' '), 'text/xml')
    return 'Actions tool exported.'
