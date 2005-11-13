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
"""CachingPolicyManager setup handlers.

$Id$
"""

from xml.dom.minidom import parseString

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import INodeExporter
from Products.GenericSetup.interfaces import INodeImporter
from Products.GenericSetup.interfaces import PURGE, UPDATE
from Products.GenericSetup.utils import PrettyDocument

_FILENAME = 'cachingpolicymgr.xml'


def importCachingPolicyManager(context):
    """ Import caching policy manager settings from an XML file.
    """
    site = context.getSite()
    mode = context.shouldPurge() and PURGE or UPDATE
    cptool = getToolByName(site, 'caching_policy_manager', None)

    body = context.readDataFile(_FILENAME)
    if body is None:
        return 'Caching policy manager: Nothing to import.'

    importer = INodeImporter(cptool, None)
    if importer is None:
        return 'Caching policy manager: Import adapter misssing.'

    importer.importNode(parseString(body).documentElement, mode=mode)
    return 'Caching policy manager settings imported.'

def exportCachingPolicyManager(context):
    """ Export caching policy manager settings as an XML file.
    """
    site = context.getSite()

    cptool = getToolByName(site, 'caching_policy_manager', None)
    if cptool is None:
        return 'Caching policy manager: Nothing to export.'

    exporter = INodeExporter(cptool)
    if exporter is None:
        return 'Caching policy manager: Export adapter misssing.'

    doc = PrettyDocument()
    doc.appendChild(exporter.exportNode(doc))
    context.writeDataFile(_FILENAME, doc.toprettyxml(' '), 'text/xml')
    return 'Caching policy manager settings exported.'
