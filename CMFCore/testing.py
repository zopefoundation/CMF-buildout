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
""" Unit test mixin classes and layers.

$Id$
"""

from Acquisition import aq_acquire
from Products.Five import i18n
from Products.Five import zcml
from zope.component import adapts
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.testmessagecatalog import TestMessageFallbackDomain
from zope.interface import implements
from zope.publisher.interfaces.http import IHTTPRequest
from zope.testing import testrunner
from zope.testing.cleanup import cleanUp


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


class BrowserLanguages(object):

    implements(IUserPreferredLanguages)
    adapts(IHTTPRequest)

    def __init__(self, context):
        self.context = context

    def getPreferredLanguages(self):
        return ('test',)


# BBB: for Five < 1.5.2
class _FallbackTranslationService(object):

    def translate(self, domain, msgid, mapping, context, target_language,
                  default):
        util = TestMessageFallbackDomain(domain)
        if context is not None:
            context = aq_acquire(context, 'REQUEST', None)
        return util.translate(msgid, mapping, context, target_language,
                              default)


class EventZCMLLayer:

    @classmethod
    def setUp(cls):
        import Products

        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('event.zcml', Products.Five)
        zcml.load_config('event.zcml', Products.CMFCore)

    @classmethod
    def tearDown(cls):
        cleanUp()


class TraversingZCMLLayer:

    @classmethod
    def setUp(cls):
        import Products.Five

        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('traversing.zcml', Products.Five)

    @classmethod
    def tearDown(cls):
        cleanUp()


class FunctionalZCMLLayer:

    @classmethod
    def setUp(cls):
        import Products

        # BBB: for Five < 1.5.2
        cls._fallback_translation_service = i18n._fallback_translation_service
        i18n._fallback_translation_service = _FallbackTranslationService()

        zcml.load_config('testing.zcml', Products.CMFCore)

    @classmethod
    def tearDown(cls):
        # BBB: for Five < 1.5.2
        i18n._fallback_translation_service = cls._fallback_translation_service

        cleanUp()


def run(test_suite):
    options = testrunner.get_options()
    options.resume_layer = None
    options.resume_number = 0
    testrunner.run_with_options(options, test_suite)
