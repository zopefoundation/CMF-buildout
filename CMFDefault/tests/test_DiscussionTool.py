##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for DiscussionTool module.

$Id$
"""

import unittest
import Testing

from Products.CMFCore.tests.base.dummy import DummyFolder
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool


class DiscussionToolTests(unittest.TestCase):

    def _makeOne(self, *args, **kw):
        from Products.CMFDefault.DiscussionTool import DiscussionTool

        return DiscussionTool(*args, **kw)

    def setUp(self):
        self.site = DummySite('site')
        self.site._setObject( 'portal_discussion', self._makeOne() )
        self.site._setObject( 'portal_membership', DummyTool() )
        self.site._setObject( 'portal_types', DummyTool() )

    def test_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider
        from Products.CMFCore.interfaces.portal_discussion \
                import portal_discussion as IDiscussionTool
        from Products.CMFDefault.DiscussionTool import DiscussionTool

        verifyClass(IActionProvider, DiscussionTool)
        verifyClass(IDiscussionTool, DiscussionTool)

    def test_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFCore.interfaces import IActionProvider
        from Products.CMFCore.interfaces import IDiscussionTool
        from Products.CMFDefault.DiscussionTool import DiscussionTool

        verifyClass(IActionProvider, DiscussionTool)
        verifyClass(IDiscussionTool, DiscussionTool)

    def test_overrideDiscussionFor(self):
        dtool = self.site.portal_discussion
        foo = self.site._setObject( 'foo', DummyFolder() )
        baz = foo._setObject( 'baz', DummyFolder() )

        dtool.overrideDiscussionFor(foo, 1)
        self.failUnless( hasattr(foo.aq_base, 'allow_discussion') )
        try:
            dtool.overrideDiscussionFor(baz, None)
        except KeyError:
            self.fail('CMF Collector issue #201 (acquisition bug): '
                      'KeyError raised')
        dtool.overrideDiscussionFor(foo, None)
        self.failIf( hasattr(foo.aq_base, 'allow_discussion') )

    def test_isDiscussionAllowedFor(self):
        # Test for Collector issue #398 (allow_discussion wrongly
        # acquired and used from parent)
        dtool = self.site.portal_discussion
        foo = self.site._setObject( 'foo', DummyFolder() )
        baz = foo._setObject( 'baz', DummyFolder() )
        dtool.overrideDiscussionFor(foo, 1)

        self.failIf(dtool.isDiscussionAllowedFor(baz))

    def test_getDiscussionFor(self):
        dtool = self.site.portal_discussion
        foo = self.site._setObject( 'foo', DummyFolder() )
        foo.allow_discussion = 1
        baz = foo._setObject( 'baz', DummyFolder() )
        baz.allow_discussion = 1

        self.failIf( hasattr(foo.aq_base, 'talkback') )
        talkback = dtool.getDiscussionFor(foo)
        self.failUnless( hasattr(foo.aq_base, 'talkback') )
        self.failIf( hasattr(baz.aq_base, 'talkback') )
        talkback = dtool.getDiscussionFor(baz)
        self.failUnless( hasattr(baz.aq_base, 'talkback'),
                         'CMF Collector issue #119 (acquisition bug): '
                         'talkback not created' )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DiscussionToolTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
