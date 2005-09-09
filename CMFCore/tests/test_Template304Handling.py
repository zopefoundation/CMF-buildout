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
""" Unit tests for status 304 handling by FSPageTemplate.

$Id$
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

try:
    ZTC_available = True
    from Testing import ZopeTestCase
    from Testing.ZopeTestCase import Functional
    from Testing.ZopeTestCase import PortalTestCase
    from Testing.ZopeTestCase.PortalTestCase import portal_name
except:
    ZTC_available = False
    class Functional:
        pass
    class PortalTestCase:
        pass
    portal_name = None

if ZTC_available:
    # set up the CMF
    ZopeTestCase.installProduct('CMFCore')
    ZopeTestCase.installProduct('CMFDefault')
    ZopeTestCase.installProduct('ZCTextIndex')
    ZopeTestCase.installProduct('CMFCalendar')
    ZopeTestCase.installProduct('CMFTopic')
    ZopeTestCase.installProduct('DCWorkflow')
    ZopeTestCase.installProduct('MailHost')
    ZopeTestCase.installProduct('PageTemplates')
    ZopeTestCase.installProduct('PythonScripts')
    ZopeTestCase.installProduct('ExternalMethod')

from App.Common import rfc1123_date
from DateTime import DateTime
from AccessControl.SecurityManagement import newSecurityManager

portal_owner = 'portal_owner'

from Products.CMFCore import CachingPolicyManager


class TestTemplate304Handling(Functional, PortalTestCase):

    def setUp(self):
        ZopeTestCase.PortalTestCase.setUp(self)

    def getPortal(self):
        # this is used by the framework to set things up
        # do not call it directly -- use self.portal instead
        if getattr(self.app, portal_name, None) is None:
            self.app.manage_addProduct['CMFDefault'].manage_addCMFSite(portal_name)
        return getattr(self.app, portal_name)

    def afterSetUp(self):
        uf = self.app.acl_users
        password = 'secret'
        uf.userFolderAddUser(portal_owner, password, ['Manager'], [])
        user = uf.getUserById(portal_owner)
        if not hasattr(user, 'aq_base'):
            user = user.__of__(uf)
        newSecurityManager(None, user)
        self.owner_auth = '%s:%s' % (portal_owner, password)
        
        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        self.portal.invokeFactory('Document', 'doc3')

        CachingPolicyManager.manage_addCachingPolicyManager(self.portal)
        cpm = self.portal.caching_policy_manager

        cpm.addPolicy(policy_id = 'policy_no_etag',
                      predicate = 'python:object.getId()=="doc1"',
                      mtime_func = '',
                      max_age_secs = 0,
                      no_cache = 0,
                      no_store = 0,
                      must_revalidate = 0,
                      vary = '',
                      etag_func = '',
                      enable_304s = 1)

        cpm.addPolicy(policy_id = 'policy_etag',
                      predicate = 'python:object.getId()=="doc2"',
                      mtime_func = '',
                      max_age_secs = 0,
                      no_cache = 0,
                      no_store = 0,
                      must_revalidate = 0,
                      vary = '',
                      etag_func = 'string:abc',
                      enable_304s = 1)

        cpm.addPolicy(policy_id = 'policy_disabled',
                      predicate = 'python:object.getId()=="doc3"',
                      mtime_func = '',
                      max_age_secs = 0,
                      no_cache = 0,
                      no_store = 0,
                      must_revalidate = 0,
                      vary = '',
                      etag_func = 'string:abc',
                      enable_304s = 0)


    def testUnconditionalGET(self):
        content_path = '/' + self.portal.doc1.absolute_url(1) + '/document_view'
        request = self.portal.REQUEST
        response = self.publish(content_path, self.owner_auth)
        self.assertEqual(response.getStatus(), 200)


    def testConditionalGETNoETag(self):
        yesterday = DateTime() - 1

        doc1 = self.portal.doc1

        content_path = '/' + doc1.absolute_url(1) + '/document_view'

        response = self.publish(content_path, env={'IF_MODIFIED_SINCE': rfc1123_date(yesterday)}, basic=self.owner_auth)
        self.assertEqual(response.getStatus(), 200)

        response = self.publish(content_path, env={'IF_MODIFIED_SINCE': rfc1123_date(doc1.modified())}, basic=self.owner_auth)
        self.assertEqual(response.getStatus(), 304)
        
        response = self.publish(content_path, env={'IF_NONE_MATCH': '"123"' }, basic=self.owner_auth)
        self.assertEqual(response.getStatus(), 200)
        
        response = self.publish(content_path, env={'IF_MODIFIED_SINCE': rfc1123_date(doc1.modified()), 'IF_NONE_MATCH': '"123"'}, basic=self.owner_auth)
        self.assertEqual(response.getStatus(), 200)
        

    def testConditionalGETETag(self):
        yesterday = DateTime() - 1

        doc2 = self.portal.doc2

        content_path = '/' + doc2.absolute_url(1) + '/document_view'
        response = self.publish(content_path, env={'IF_MODIFIED_SINCE': rfc1123_date(yesterday)}, basic=self.owner_auth)
        self.assertEqual(response.getStatus(), 200)

        response = self.publish(content_path, env={'IF_MODIFIED_SINCE': rfc1123_date(doc2.modified())}, basic=self.owner_auth)
        self.assertEqual(response.getStatus(), 200) # should be 200 because we also have an etag

        response = self.publish(content_path, env={'IF_NONE_MATCH': '"123"' }, basic=self.owner_auth)
        self.assertEqual(response.getStatus(), 200)

        # etag matches, no modification time in request
        response = self.publish(content_path, env={'IF_NONE_MATCH': '"abc"' }, basic=self.owner_auth)
        self.assertEqual(response.getStatus(), 304)
        
        response = self.publish(content_path, env={'IF_MODIFIED_SINCE': rfc1123_date(doc2.modified()), 'IF_NONE_MATCH': '"123"'}, basic=self.owner_auth)
        self.assertEqual(response.getStatus(), 200)

        response = self.publish(content_path, env={'IF_MODIFIED_SINCE': rfc1123_date(yesterday), 'IF_NONE_MATCH': '"abc"'}, basic=self.owner_auth)
        self.assertEqual(response.getStatus(), 200)
        
        # etag matches, valid modification time in request
        response = self.publish(content_path, env={'IF_MODIFIED_SINCE': rfc1123_date(doc2.modified()), 'IF_NONE_MATCH': '"abc"'}, basic=self.owner_auth)
        self.assertEqual(response.getStatus(), 304)

        
    def testConditionalGETDisabled(self):
        yesterday = DateTime() - 1

        doc3 = self.portal.doc3
        content_path = '/' + doc3.absolute_url(1) + '/document_view'

        response = self.publish(content_path, env={'IF_NONE_MATCH': '"abc"' }, basic=self.owner_auth)
        self.assertEqual(response.getStatus(), 200)
        
        response = self.publish(content_path, env={'IF_MODIFIED_SINCE': rfc1123_date(doc3.modified()), 'IF_NONE_MATCH': '"abc"'}, basic=self.owner_auth)
        self.assertEqual(response.getStatus(), 200)
        

def test_suite():
    if ZTC_available:
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestTemplate304Handling))
        return suite
    else:
        print 'Warning: test_Template304Handling.py requires ZopeTestCase to run.'
        print 'ZopeTestCase is available from http://www.zope.org/Members/shh/ZopeTestCase and ships with Zope 2.8+'

if __name__ == '__main__':
    framework()
