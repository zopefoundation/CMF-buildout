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
""" Unit tests mixin classes.

$Id$
"""

class ConformsToFolder:

    def test_folder_z2interfaces(self):
        from Interface.Verify import verifyClass
        from webdav.WriteLockInterface import WriteLockInterface
        from Products.CMFCore.interfaces.Dynamic \
                import DynamicType as IDynamicType
        from Products.CMFCore.interfaces.Folderish \
                import Folderish as IFolderish

        verifyClass(IDynamicType, self._getTargetClass())
        verifyClass(IFolderish, self._getTargetClass())
        verifyClass(WriteLockInterface, self._getTargetClass())

    def test_folder_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from webdav.interfaces import IWriteLock
        from Products.CMFCore.interfaces import IDynamicType
        from Products.CMFCore.interfaces import IFolderish
        from Products.CMFCore.interfaces import IMutableMinimalDublinCore

        verifyClass(IDynamicType, self._getTargetClass())
        verifyClass(IFolderish, self._getTargetClass())
        verifyClass(IMutableMinimalDublinCore, self._getTargetClass())
        verifyClass(IWriteLock, self._getTargetClass())


class ConformsToContent:

    def test_content_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFCore.interfaces.Contentish \
                import Contentish as IContentish
        from Products.CMFCore.interfaces.DublinCore \
                import CatalogableDublinCore as ICatalogableDublinCore
        from Products.CMFCore.interfaces.DublinCore \
                import DublinCore as IDublinCore
        from Products.CMFCore.interfaces.DublinCore \
                import MutableDublinCore as IMutableDublinCore
        from Products.CMFCore.interfaces.Dynamic \
                import DynamicType as IDynamicType

        verifyClass(ICatalogableDublinCore, self._getTargetClass())
        verifyClass(IContentish, self._getTargetClass())
        verifyClass(IDublinCore, self._getTargetClass())
        verifyClass(IDynamicType, self._getTargetClass())
        verifyClass(IMutableDublinCore, self._getTargetClass())

    def test_content_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFCore.interfaces import ICatalogableDublinCore
        from Products.CMFCore.interfaces import IContentish
        from Products.CMFCore.interfaces import IDublinCore
        from Products.CMFCore.interfaces import IDynamicType
        from Products.CMFCore.interfaces import IMutableDublinCore
        from Products.GenericSetup.interfaces import IDAVAware

        verifyClass(ICatalogableDublinCore, self._getTargetClass())
        verifyClass(IContentish, self._getTargetClass())
        verifyClass(IDAVAware, self._getTargetClass())
        verifyClass(IDublinCore, self._getTargetClass())
        verifyClass(IDynamicType, self._getTargetClass())
        verifyClass(IMutableDublinCore, self._getTargetClass())
