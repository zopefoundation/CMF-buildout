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
"""CachingPolicyManager setup handler unit tests.

$Id$
"""

import unittest
import Testing

from Products.GenericSetup.tests.common import BaseRegistryTests
from Products.GenericSetup.tests.common import DummyExportContext
from Products.GenericSetup.tests.common import DummyImportContext


class _CachingPolicyManagerSetup(BaseRegistryTests):

    POLICY_ID = 'policy_id'
    PREDICATE = "python:object.getId() == 'foo'"
    MTIME_FUNC = "object/modified"
    MAX_AGE_SECS = 60
    VARY = "Test"
    ETAG_FUNC = "object/getETag"
    S_MAX_AGE_SECS = 120
    PRE_CHECK = 42
    POST_CHECK = 43

    _EMPTY_EXPORT = """\
<?xml version="1.0"?>
<caching-policies>
</caching-policies>
"""

    _WITH_POLICY_EXPORT = """\
<?xml version="1.0"?>
<caching-policies>
 <caching-policy
    policy_id="%s"
    predicate="%s"
    mtime_func="%s"
    vary="%s"
    etag_func="%s"
    max_age_secs="%d"
    s_max_age_secs="%d"
    pre_check="%d"
    post_check="%d"
    last_modified="False"
    no_cache="True"
    no_store="True"
    must_revalidate="True"
    proxy_revalidate="True"
    no_transform="True"
    public="True"
    private="True"
    enable_304s="True"
    />
</caching-policies>
""" % (POLICY_ID,
       PREDICATE,
       MTIME_FUNC,
       VARY,
       ETAG_FUNC,
       MAX_AGE_SECS,
       S_MAX_AGE_SECS,
       PRE_CHECK,
       POST_CHECK,
      )

    def _initSite(self, with_policy=False):
        from OFS.Folder import Folder
        from Products.CMFCore.CachingPolicyManager import CachingPolicyManager

        self.root.site = Folder(id='site')
        site = self.root.site
        mgr = CachingPolicyManager()
        site._setObject( mgr.getId(), mgr )

        if with_policy:
            mgr.addPolicy( policy_id=self.POLICY_ID
                         , predicate=self.PREDICATE
                         , mtime_func=self.MTIME_FUNC
                         , max_age_secs=self.MAX_AGE_SECS
                         , no_cache=True
                         , no_store=True
                         , must_revalidate=True
                         , vary=self.VARY
                         , etag_func=self.ETAG_FUNC
                         , s_max_age_secs=self.S_MAX_AGE_SECS
                         , proxy_revalidate=True
                         , public=True
                         , private=True
                         , no_transform=True
                         , enable_304s=True
                         , last_modified=False
                         , pre_check=self.PRE_CHECK
                         , post_check=self.POST_CHECK
                         )
        return site

class CachingPolicyManagerExportConfiguratorTests(_CachingPolicyManagerSetup):

    def _getTargetClass(self):
        from Products.CMFSetup.cachingpolicymgr \
                import CachingPolicyManagerExportConfigurator

        return CachingPolicyManagerExportConfigurator

    def test_generateXML_empty(self):
        site = self._initSite(with_policy=False)
        configurator = self._makeOne(site).__of__(site)

        self._compareDOM(configurator.generateXML(), self._EMPTY_EXPORT)

    def test_generateXML_with_policy(self):
        site = self._initSite(with_policy=True)
        configurator = self._makeOne(site).__of__(site)

        self._compareDOM(configurator.generateXML(), self._WITH_POLICY_EXPORT)


class CachingPolicyManagerImportConfiguratorTests(_CachingPolicyManagerSetup):

    def _getTargetClass(self):
        from Products.CMFSetup.cachingpolicymgr \
                import CachingPolicyManagerImportConfigurator

        return CachingPolicyManagerImportConfigurator

    def test_parseXML_empty(self):
        site = self._initSite(with_policy=False)
        configurator = self._makeOne(site)
        cpm_info = configurator.parseXML(self._EMPTY_EXPORT)

        self.assertEqual(len(cpm_info['policies']), 0)

    def test_parseXML_with_policy(self):
        site = self._initSite(with_policy=False)
        configurator = self._makeOne(site)
        cpm_info = configurator.parseXML(self._WITH_POLICY_EXPORT)

        self.assertEqual(len(cpm_info['policies']), 1)

        info = cpm_info['policies'][0]
        self.assertEqual(info['policy_id'], self.POLICY_ID)
        self.assertEqual(info['predicate'], self.PREDICATE)
        self.assertEqual(info['mtime_func'], self.MTIME_FUNC)
        self.assertEqual(info['vary'], self.VARY)
        self.assertEqual(info['etag_func'], self.ETAG_FUNC)
        self.assertEqual(info['max_age_secs'], self.MAX_AGE_SECS)
        self.assertEqual(info['s_max_age_secs'], self.S_MAX_AGE_SECS)
        self.assertEqual(info['pre_check'], self.PRE_CHECK)
        self.assertEqual(info['post_check'], self.POST_CHECK)
        self.assertEqual(info['last_modified'], False)
        self.assertEqual(info['no_cache'], True)
        self.assertEqual(info['no_store'], True)
        self.assertEqual(info['must_revalidate'], True)
        self.assertEqual(info['proxy_revalidate'], True)
        self.assertEqual(info['no_transform'], True)
        self.assertEqual(info['public'], True)
        self.assertEqual(info['private'], True)
        self.assertEqual(info['enable_304s'], True)

class Test_exportCachingPolicyManager(_CachingPolicyManagerSetup):

    def test_empty(self):
        from Products.CMFSetup.cachingpolicymgr \
            import exportCachingPolicyManager

        site = self._initSite(with_policy=False)
        context = DummyExportContext(site)
        exportCachingPolicyManager(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'cachingpolicymgr.xml')
        self._compareDOM(text, self._EMPTY_EXPORT)
        self.assertEqual(content_type, 'text/xml')

    def test_with_policy(self):
        from Products.CMFSetup.cachingpolicymgr \
            import exportCachingPolicyManager

        site = self._initSite(with_policy=True)
        context = DummyExportContext(site)
        exportCachingPolicyManager(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'cachingpolicymgr.xml')
        self._compareDOM(text, self._WITH_POLICY_EXPORT)
        self.assertEqual(content_type, 'text/xml')


class Test_importCachingPolicyManager(_CachingPolicyManagerSetup):

    def test_normal(self):
        from Products.CMFSetup.cachingpolicymgr \
            import importCachingPolicyManager

        site = self._initSite(with_policy=False)
        cpm = site.caching_policy_manager
        self.assertEqual(len(cpm.listPolicies()), 0)

        context = DummyImportContext(site)
        context._files['cachingpolicymgr.xml'] = self._WITH_POLICY_EXPORT
        importCachingPolicyManager(context)

        self.assertEqual(len(cpm.listPolicies()), 1)
        policy_id, policy = cpm.listPolicies()[0]

        self.assertEqual(policy.getPolicyId(), self.POLICY_ID)
        self.assertEqual(policy.getPredicate(), self.PREDICATE)
        self.assertEqual(policy.getMTimeFunc(), self.MTIME_FUNC)
        self.assertEqual(policy.getVary(), self.VARY)
        self.assertEqual(policy.getETagFunc(), self.ETAG_FUNC)
        self.assertEqual(policy.getMaxAgeSecs(), self.MAX_AGE_SECS)
        self.assertEqual(policy.getSMaxAgeSecs(), self.S_MAX_AGE_SECS)
        self.assertEqual(policy.getPreCheck(), self.PRE_CHECK)
        self.assertEqual(policy.getPostCheck(), self.POST_CHECK)
        self.assertEqual(policy.getLastModified(), False)
        self.assertEqual(policy.getNoCache(), True)
        self.assertEqual(policy.getNoStore(), True)
        self.assertEqual(policy.getMustRevalidate(), True)
        self.assertEqual(policy.getProxyRevalidate(), True)
        self.assertEqual(policy.getNoTransform(), True)
        self.assertEqual(policy.getPublic(), True)
        self.assertEqual(policy.getPrivate(), True)
        self.assertEqual(policy.getEnable304s(), True)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CachingPolicyManagerExportConfiguratorTests),
        unittest.makeSuite(CachingPolicyManagerImportConfiguratorTests),
        unittest.makeSuite(Test_exportCachingPolicyManager),
        unittest.makeSuite(Test_importCachingPolicyManager),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
