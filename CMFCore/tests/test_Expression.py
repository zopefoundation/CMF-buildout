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
""" Unit tests for Expression module.

$Id$
"""

import unittest
import Testing

from zope.component import getSiteManager

from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.Expression import Expression
from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.tests.base.dummy import DummyTool as DummyMembershipTool
from Products.CMFCore.tests.base.testcase import SecurityTest


class ExpressionTests( SecurityTest ):

    def setUp( self ):

        SecurityTest.setUp(self)
        root = self.root
        root._setObject('portal', DummyContent('portal', url='url_portal'))
        portal = self.portal = root.portal
        self.folder = DummyContent('foo', url='url_foo')
        self.object = DummyContent('bar', url='url_bar')
        self.ai = ActionInformation(id='view'
                                  , title='View'
                                  , action=Expression(
                  text='view')
                                  , condition=Expression(
                  text='member')
                                  , category='global'
                                  , visible=1)

    def test_anonymous_ec(self):
        sm = getSiteManager()
        self.portal.portal_membership = DummyMembershipTool()
        sm.registerUtility(self.portal.portal_membership, IMembershipTool)
        ec = createExprContext(self.folder, self.portal, self.object)
        member = ec.contexts['member']
        self.failIf(member)

    def test_authenticatedUser_ec(self):
        sm = getSiteManager()
        self.portal.portal_membership = DummyMembershipTool(anon=0)
        sm.registerUtility(self.portal.portal_membership, IMembershipTool)
        ec = createExprContext(self.folder, self.portal, self.object)
        member = ec.contexts['member']
        self.assertEqual(member.getId(), 'dummy')

    def test_ec_context(self):
        sm = getSiteManager()
        self.portal.portal_membership = DummyMembershipTool()
        sm.registerUtility(self.portal.portal_membership, IMembershipTool)
        ec = createExprContext(self.folder, self.portal, self.object)
        object = ec.contexts['object']
        portal = ec.contexts['portal']
        folder = ec.contexts['folder']
        self.failUnless(object)
        self.assertEqual(object.id, 'bar')
        self.assertEqual(object.absolute_url(), 'url_bar')
        self.failUnless(portal)
        self.assertEqual(portal.id, 'portal')
        self.assertEqual(portal.absolute_url(), 'url_portal')
        self.failUnless(folder)
        self.assertEqual(folder.id, 'foo')
        self.assertEqual(folder.absolute_url(), 'url_foo')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ExpressionTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
