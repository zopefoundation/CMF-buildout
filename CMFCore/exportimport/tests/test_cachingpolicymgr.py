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
"""Caching policy manager node adapter unit tests.

$Id$
"""

import unittest
import Testing

from Products.CMFCore.tests.base.testcase import PlacelessSetup
from Products.GenericSetup.testing import NodeAdapterTestCase


_CP_XML = """\
<caching-policy name="foo_policy" enable_304s="False" etag_func=""
   last_modified="True" max_age_secs="0" mtime_func="object/modified"
   must_revalidate="False" no_cache="False" no_store="False"
   no_transform="False" predicate="python:1" private="False"
   proxy_revalidate="False" public="False" vary=""/>
"""

_CPM_XML = """\
<object name="caching_policy_manager" meta_type="CMF Caching Policy Manager">
 <caching-policy name="foo_policy" enable_304s="False" etag_func=""
    last_modified="True" max_age_secs="600" mtime_func="object/modified"
    must_revalidate="False" no_cache="False" no_store="False"
    no_transform="False"
    predicate="python:object.getPortalTypeName() == 'Foo'" private="False"
    proxy_revalidate="False" public="False" vary=""/>
</object>
"""


class CachingPolicyNodeAdapterTests(PlacelessSetup, NodeAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFCore.exportimport.cachingpolicymgr \
                import CachingPolicyNodeAdapter

        return CachingPolicyNodeAdapter

    def setUp(self):
        from Products.CMFCore.CachingPolicyManager import CachingPolicy
        import Products.CMFCore.exportimport
        import Products.Five
        from Products.Five import zcml

        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore.exportimport)

        self._obj = CachingPolicy('foo_policy', max_age_secs=0)
        self._XML = _CP_XML


class CachingPolicyManagerNodeAdapterTests(PlacelessSetup,
                                           NodeAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFCore.exportimport.cachingpolicymgr \
                import CachingPolicyManagerNodeAdapter

        return CachingPolicyManagerNodeAdapter

    def _populate(self, obj):
        obj.addPolicy('foo_policy',
                      'python:object.getPortalTypeName() == \'Foo\'',
                      'object/modified', 600, 0, 0, 0, '', '')

    def setUp(self):
        from Products.CMFCore.CachingPolicyManager import CachingPolicyManager
        import Products.CMFCore.exportimport
        import Products.Five
        from Products.Five import zcml

        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore.exportimport)

        self._obj = CachingPolicyManager()
        self._XML = _CPM_XML


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CachingPolicyNodeAdapterTests),
        unittest.makeSuite(CachingPolicyManagerNodeAdapterTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
