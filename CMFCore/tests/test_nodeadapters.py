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
"""CMFCore node adapter unit tests.

$Id$
"""

import unittest
import Testing

import Products
from Products.Five import zcml
from Products.GenericSetup.testing import NodeAdapterTestCase
from zope.app.tests.placelesssetup import PlacelessSetup


_COOKIECRUMBLER_XML = """\
<object name="foo_cookiecrumbler" meta_type="Cookie Crumbler">
 <property name="auth_cookie">__ac</property>
 <property name="name_cookie">__ac_name</property>
 <property name="pw_cookie">__ac_password</property>
 <property name="persist_cookie">__ac_persistent</property>
 <property name="auto_login_page">login_form</property>
 <property name="logout_page">logged_out</property>
 <property name="unauth_page"></property>
 <property name="local_cookie_path">False</property>
 <property name="cache_header_value">private</property>
 <property name="log_username">True</property>
</object>
"""


class CookieCrumblerNodeAdapterTests(PlacelessSetup, NodeAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFCore.nodeadapters import CookieCrumblerNodeAdapter

        return CookieCrumblerNodeAdapter

    def setUp(self):
        from Products.CMFCore.CookieCrumbler import CookieCrumbler

        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore)

        self._obj = CookieCrumbler('foo_cookiecrumbler')
        self._XML = _COOKIECRUMBLER_XML


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CookieCrumblerNodeAdapterTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
