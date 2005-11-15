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
"""Cookie crumbler setup handler unit tests.

$Id$
"""

import unittest
import Testing

from OFS.Folder import Folder

from Products.CMFCore.CookieCrumbler import CookieCrumbler

from common import BaseRegistryTests
from common import DummyExportContext
from common import DummyImportContext


class _CookieCrumblerSetup(BaseRegistryTests):

    def _initSite(self, use_changed=False):
        self.root.site = Folder(id='site')
        site = self.root.site
        cc = site.cookie_authentication = CookieCrumbler('foo_cookiecrumbler')
 
        if use_changed:
            cc.auth_cookie = 'value1'
            cc.cache_header_value = 'value2'
            cc.name_cookie = 'value3'
            cc.log_username = 0
            cc.persist_cookie = 'value4'
            cc.pw_cookie = 'value5'
            cc.local_cookie_path = 1
            cc.auto_login_page = 'value6'
            cc.unauth_page = 'value7'
            cc.logout_page = 'value8'

        return site


class CookieCrumblerExportConfiguratorTests(_CookieCrumblerSetup):

    def _getTargetClass(self):
        from Products.CMFSetup.cookieauth \
                import CookieCrumblerExportConfigurator

        return CookieCrumblerExportConfigurator

    def test_generateXML_default(self):
        site = self._initSite()
        configurator = self._makeOne(site).__of__(site)

        self._compareDOM(configurator.generateXML(), _DEFAULT_EXPORT)

    def test_generateXML_changed(self):
        site = self._initSite(use_changed=True)
        configurator = self._makeOne(site).__of__(site)

        self._compareDOM(configurator.generateXML(), _CHANGED_EXPORT)


class CookieCrumblerImportConfiguratorTests(_CookieCrumblerSetup):

    def _getTargetClass(self):
        from Products.CMFSetup.cookieauth \
                import CookieCrumblerImportConfigurator

        return CookieCrumblerImportConfigurator

    def test_parseXML_default(self):
        site = self._initSite()
        configurator = self._makeOne(site)
        cc_info = configurator.parseXML(_DEFAULT_EXPORT)

        self.assertEqual(len(cc_info['properties']), 10)

        info = cc_info['properties'][0]
        self.assertEqual(info['id'], 'auth_cookie')
        self.assertEqual(info['value'], '__ac')
        self.assertEqual(len(info['elements']), 0)

        info = cc_info['properties'][1]
        self.assertEqual(info['id'], 'name_cookie')
        self.assertEqual(info['value'], '__ac_name')
        self.assertEqual(len(info['elements']), 0)

    def test_parseXML_changed(self):
        site = self._initSite()
        configurator = self._makeOne(site)
        cc_info = configurator.parseXML(_CHANGED_EXPORT)

        self.assertEqual(len(cc_info['properties']), 10)

        info = cc_info['properties'][0]
        self.assertEqual(info['id'], 'auth_cookie')
        self.assertEqual(info['value'], 'value1')
        self.assertEqual(len(info['elements']), 0)

        info = cc_info['properties'][1]
        self.assertEqual(info['id'], 'name_cookie')
        self.assertEqual(info['value'], 'value3')
        self.assertEqual(len(info['elements']), 0)


_DEFAULT_EXPORT = """\
<?xml version="1.0"?>
<object name="foo_cookiecrumbler" meta_type="Cookie Crumbler">
  <property name="auth_cookie">__ac</property>
  <property name="name_cookie">__ac_name</property>
  <property name="pw_cookie">__ac_password</property>
  <property name="persist_cookie">__ac_persistent</property>
  <property name="auto_login_page">login_form</property>
  <property name="logout_page">logged_out</property>
  <property name="unauth_page"></property>
  <property name="local_cookie_path">0</property>
  <property name="cache_header_value">private</property>
  <property name="log_username">1</property>
</object>
"""

_CHANGED_EXPORT = """\
<?xml version="1.0"?>
<object name="foo_cookiecrumbler" meta_type="Cookie Crumbler">
  <property name="auth_cookie">value1</property>
  <property name="name_cookie">value3</property>
  <property name="pw_cookie">value5</property>
  <property name="persist_cookie">value4</property>
  <property name="auto_login_page">value6</property>
  <property name="logout_page">value8</property>
  <property name="unauth_page">value7</property>
  <property name="local_cookie_path">1</property>
  <property name="cache_header_value">value2</property>
  <property name="log_username">0</property>
</object>
"""


class Test_exportCookieCrumbler(_CookieCrumblerSetup):

    def test_unchanged(self):
        from Products.CMFSetup.cookieauth import exportCookieCrumbler

        site = self._initSite(use_changed=False)
        context = DummyExportContext(site)
        exportCookieCrumbler(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'cookieauth.xml')
        self._compareDOM(text, _DEFAULT_EXPORT)
        self.assertEqual(content_type, 'text/xml')

    def test_changed(self):
        from Products.CMFSetup.cookieauth import exportCookieCrumbler

        site = self._initSite(use_changed=True)
        context = DummyExportContext(site)
        exportCookieCrumbler(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'cookieauth.xml')
        self._compareDOM(text, _CHANGED_EXPORT)
        self.assertEqual(content_type, 'text/xml')


class Test_importCookieCrumbler(_CookieCrumblerSetup):

    def test_normal(self):
        from Products.CMFSetup.cookieauth import importCookieCrumbler

        site = self._initSite()
        cc = site.cookie_authentication

        context = DummyImportContext(site)
        context._files['cookieauth.xml'] = _CHANGED_EXPORT
        importCookieCrumbler(context)

        self.assertEqual( cc.auth_cookie, 'value1' )
        self.assertEqual( cc.cache_header_value, 'value2' )
        self.assertEqual( cc.name_cookie, 'value3' )
        self.assertEqual( cc.log_username, 0 )
        self.assertEqual( cc.persist_cookie, 'value4' )
        self.assertEqual( cc.pw_cookie, 'value5' )
        self.assertEqual( cc.local_cookie_path, 1 )
        self.assertEqual( cc.auto_login_page, 'value6' )
        self.assertEqual( cc.unauth_page, 'value7' )
        self.assertEqual( cc.logout_page, 'value8' )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CookieCrumblerExportConfiguratorTests),
        unittest.makeSuite(CookieCrumblerImportConfiguratorTests),
        unittest.makeSuite(Test_exportCookieCrumbler),
        unittest.makeSuite(Test_importCookieCrumbler),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
