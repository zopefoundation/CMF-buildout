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
"""Site properties node adapters.

$Id$
"""

from Products.GenericSetup.interfaces import PURGE
from Products.GenericSetup.utils import NodeAdapterBase
from Products.GenericSetup.utils import PropertyManagerHelpers

from Products.CMFCore.interfaces import ISiteRoot


class PropertiesNodeAdapter(NodeAdapterBase, PropertyManagerHelpers):

    """Node im- and exporter for properties.
    """

    __used_for__ = ISiteRoot

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._doc.createElement('site')
        node.appendChild(self._extractProperties())
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        if mode == PURGE:
            self._purgeProperties()

        self._initProperties(node, mode)
