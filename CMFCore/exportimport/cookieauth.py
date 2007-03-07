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

from zope.component import adapts
from zope.component import getSiteManager
from zope.component import getUtility
from zope.component import queryUtility

from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase

from Products.CMFCore.interfaces import ICookieCrumbler


class CookieCrumblerXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):

    """XML im- and exporter for CookieCrumbler.
    """

    adapts(ICookieCrumbler, ISetupEnviron)

    _LOGGER_ID = 'cookies'

    name = 'cookieauth'

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())

        self._logger.info('Cookie crumbler exported.')
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()

        self._initProperties(node)

        self._logger.info('Cookie crumbler imported.')


def importCookieCrumbler(context):
    """Import cookie crumbler settings from an XML file.
    """
    sm = getSiteManager(context.getSite())
    tool = sm.getUtility(ICookieCrumbler)

    importObjects(tool, '', context)

def exportCookieCrumbler(context):
    """Export cookie crumbler settings as an XML file.
    """
    sm = getSiteManager(context.getSite())
    tool = queryUtility(ICookieCrumbler)
    if tool is None:
        logger = context.getLogger('cookies')
        logger.info('Nothing to export.')
        return

    exportObjects(tool, '', context)
