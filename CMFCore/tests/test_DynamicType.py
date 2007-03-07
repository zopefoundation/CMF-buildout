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
""" Unit tests for DynamicType module.

$Id$
"""

import unittest
import Testing

from StringIO import StringIO

from Acquisition import Implicit
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse

from zope.component import getSiteManager

from Products.CMFCore.DynamicType import DynamicType
from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFCore.interfaces import ITypesTool
from Products.CMFCore.interfaces import IURLTool
from Products.CMFCore.tests.base.dummy import DummyObject
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFCore.tests.base.testcase import SecurityRequestTest
from Products.CMFCore.tests.base.tidata import FTIDATA_CMF15
from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI
from Products.CMFCore.TypesTool import TypesTool

import zope.component
from zope.testing.cleanup import CleanUp
from zope.interface import alsoProvides
from zope.component.interfaces import IDefaultViewName
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserView
from Products.Five.browser import BrowserView

def defineDefaultViewName(name, for_=None):
    zope.component.provideAdapter(name, (for_, IBrowserRequest),
                                  IDefaultViewName, '')


class DummyContent(DynamicType, Implicit):
    """ Basic dynamic content class.
    """

    portal_type = 'Dummy Content 15'


class DummyView(BrowserView):
    """This is a view"""


class DynamicTypeTests(unittest.TestCase):

    def setUp(self):
        sm = getSiteManager()
        self.site = DummySite('site')
        self.site._setObject( 'portal_types', TypesTool() )
        sm.registerUtility(self.site.portal_types, ITypesTool)
        fti = FTIDATA_CMF15[0].copy()
        self.site.portal_types._setObject( 'Dummy Content 15', FTI(**fti) )
        self.site._setObject( 'foo', DummyContent() )

    def test_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFCore.interfaces.Dynamic \
                import DynamicType as IDynamicType

        verifyClass(IDynamicType, DynamicType)

    def test_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFCore.interfaces import IDynamicType
        verifyClass(IDynamicType, DynamicType)

class DynamicTypeDefaultTraversalTests(CleanUp, unittest.TestCase):

    def setUp(self):
        self.site = DummySite('site')
        self.site._setObject( 'portal_types', TypesTool() )
        fti = FTIDATA_CMF15[0].copy()
        self.site.portal_types._setObject( 'Dummy Content 15', FTI(**fti) )
        self.site._setObject( 'foo', DummyContent() )
        dummy_view = self.site._setObject( 'dummy_view', DummyObject() )

    def test_default_view_from_fti(self):
        response = HTTPResponse()
        environment = { 'URL': '',
                        'PARENTS': [self.site],
                        'REQUEST_METHOD': 'GET',
                        'SERVER_PORT': '80',
                        'REQUEST_METHOD': 'GET',
                        'steps': [],
                        'SERVER_NAME': 'localhost',
                        '_hacked_path': 0 }
        r = HTTPRequest(StringIO(), environment, response)
        r.other.update(environment)
        alsoProvides(r, IBrowserRequest)

        r.traverse('foo')
        self.assertEqual( r.URL, '/foo/dummy_view' )
        self.assertEqual( r.response.base, '/foo/',
                          'CMF Collector issue #192 (wrong base): %s'
                          % (r.response.base or 'empty',) )

    def test_default_viewname_but_no_view_doesnt_override_fti(self):
        response = HTTPResponse()
        environment = { 'URL': '',
                        'PARENTS': [self.site],
                        'REQUEST_METHOD': 'GET',
                        'SERVER_PORT': '80',
                        'REQUEST_METHOD': 'GET',
                        'steps': [],
                        'SERVER_NAME': 'localhost',
                        '_hacked_path': 0 }
        r = HTTPRequest(StringIO(), environment, response)
        r.other.update(environment)
        alsoProvides(r, IBrowserRequest)

        # we define a Zope3-style default view name, but no
        # corresponding view, no change in behaviour expected
        defineDefaultViewName('index.html', DummyContent)
        r.traverse('foo')
        self.assertEqual( r.URL, '/foo/dummy_view' )
        self.assertEqual( r.response.base, '/foo/' )

    def test_default_viewname_overrides_fti(self):
        response = HTTPResponse()
        environment = { 'URL': '',
                        'PARENTS': [self.site],
                        'REQUEST_METHOD': 'GET',
                        'SERVER_PORT': '80',
                        'REQUEST_METHOD': 'GET',
                        'steps': [],
                        'SERVER_NAME': 'localhost',
                        '_hacked_path': 0 }
        r = HTTPRequest(StringIO(), environment, response)
        r.other.update(environment)
        alsoProvides(r, IBrowserRequest)

        # we define a Zope3-style default view name for which a view
        # actually exists
        defineDefaultViewName('index.html', DummyContent)
        zope.component.provideAdapter(
            DummyView, (DummyContent, IBrowserRequest), IBrowserView,
            'index.html')

        r.traverse('foo')
        self.assertEqual( r.URL, '/foo/index.html' )
        self.assertEqual( r.response.base, '/foo/' )


class DynamicTypeSecurityTests(SecurityRequestTest):

    def setUp(self):
        SecurityRequestTest.setUp(self)
        self.site = DummySite('site').__of__(self.root)
        sm = getSiteManager()
        self.site._setObject( 'portal_membership', DummyTool() )
        sm.registerUtility(self.site.portal_membership, IMembershipTool)
        self.site._setObject( 'portal_types', TypesTool() )
        sm.registerUtility(self.site.portal_types, ITypesTool)
        self.site._setObject( 'portal_url', DummyTool() )
        sm.registerUtility(self.site.portal_url, IURLTool)
        fti = FTIDATA_CMF15[0].copy()
        self.site.portal_types._setObject( 'Dummy Content 15', FTI(**fti) )
        self.site._setObject( 'foo', DummyContent() )

    def test_getTypeInfo(self):
        foo = self.site.foo
        self.assertEqual( foo.getTypeInfo().getId(), 'Dummy Content 15' )

    def test_getActionInfo(self):
        foo = self.site.foo
        self.assertEqual( foo.getActionInfo('object/view')['id'], 'view' )

        # The following is nasty, but I want to make sure the ValueError
        # carries some useful information
        INVALID_ID = 'invalid_id'
        try:
            rval = foo.getActionInfo('object/%s' % INVALID_ID)
        except ValueError, e:
            message = e.args[0]
            detail = '"%s" does not offer action "%s"' % (message, INVALID_ID)
            self.failUnless(message.find(INVALID_ID) != -1, detail)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DynamicTypeTests),
        unittest.makeSuite(DynamicTypeDefaultTraversalTests),
        unittest.makeSuite(DynamicTypeSecurityTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
