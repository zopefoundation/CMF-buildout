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
"""Cookie crumbler node adapter unit tests.

$Id: test_cookieauth.py 39963 2005-11-07 19:06:45Z tseaver $
"""

import unittest
import Testing

from Products.CMFCore.tests.base.testcase import PlacelessSetup
from Products.GenericSetup.testing import NodeAdapterTestCase


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
        from Products.CMFCore.exportimport.cookieauth \
                import CookieCrumblerNodeAdapter

        return CookieCrumblerNodeAdapter

    def setUp(self):
        from Products.CMFCore.CookieCrumbler import CookieCrumbler
        import Products.CMFCore.exportimport
        import Products.Five
        from Products.Five import zcml

        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore.exportimport)

        self._obj = CookieCrumbler('foo_cookiecrumbler')
        self._XML = _COOKIECRUMBLER_XML


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CookieCrumblerNodeAdapterTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
