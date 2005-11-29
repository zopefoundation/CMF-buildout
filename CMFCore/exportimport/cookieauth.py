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
"""Cookie crumbler xml adapters and setup handlers.

$Id$
"""

from zope.app import zapi

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import PURGE
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase

from Products.CMFCore.interfaces import ICookieCrumbler
from Products.CMFCore.utils import getToolByName

_FILENAME = 'cookieauth.xml'


class CookieCrumblerXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):

    """XML im- and exporter for CookieCrumbler.
    """

    __used_for__ = ICookieCrumbler

    _LOGGER_ID = 'cookies'

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())

        self._logger.info('Cookie crumbler exported.')
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        if mode == PURGE:
            self._purgeProperties()

        self._initProperties(node, mode)

        self._logger.info('Cookie crumbler imported.')


def importCookieCrumbler(context):
    """Import cookie crumbler settings from an XML file.
    """
    site = context.getSite()
    logger = context.getLogger('cookies')
    tool = getToolByName(site, 'cookie_authentication')

    body = context.readDataFile(_FILENAME)
    if body is None:
        logger.info('Nothing to import.')
        return

    importer = zapi.queryMultiAdapter((tool, context), IBody)
    if importer is None:
        logger.warning('Import adapter misssing.')
        return

    importer.body = body

def exportCookieCrumbler(context):
    """Export cookie crumbler settings as an XML file.
    """
    site = context.getSite()
    logger = context.getLogger('cookies')
    tool = getToolByName(site, 'cookie_authentication', None)
    if tool is None:
        logger.info('Nothing to export.')
        return

    exporter = zapi.queryMultiAdapter((tool, context), IBody)
    if exporter is None:
        logger.warning('Export adapter misssing.')
        return

    context.writeDataFile(_FILENAME, exporter.body, exporter.mime_type)
