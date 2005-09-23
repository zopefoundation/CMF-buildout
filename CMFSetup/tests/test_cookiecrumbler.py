##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Cookiecrumbler properties export / import unit tests.

$Id: test_cookiecrumbler.py 37061 2005-06-15 14:17:41Z tseaver $
"""
import unittest
import Testing
import Zope2
Zope2.startup()

from OFS.Folder import Folder

from common import BaseRegistryTests
from common import DummyExportContext
from common import DummyImportContext


_DEFAULT_EXPORT = """\
<?xml version="1.0"?>
<cookiecrumbler auth_cookie="__ac" cache_header_value="private"
    name_cookie="__ac_name" log_username="1"
    persist_cookie="__ac_persistent"
    pw_cookie="__ac_password" local_cookie_path="0"
    auto_login_page="login_form" unauth_page=""
    logout_page="logged_out"/>
"""

_CHANGED_EXPORT = """\
<?xml version="1.0"?>
<cookiecrumbler auth_cookie="value1" cache_header_value="value2"
    name_cookie="value3" log_username="0"
    persist_cookie="value4"
    pw_cookie="value5" local_cookie_path="1"
    auto_login_page="value6" unauth_page="value7"
    logout_page="value8"/>
"""

class DummySite(Folder):
    pass


class DummyCookieCrumbler:

    auth_cookie = '__ac'
    cache_header_value = 'private'
    name_cookie = '__ac_name'
    log_username = 1
    persist_cookie = '__ac_persistent'
    pw_cookie = '__ac_password'
    local_cookie_path = 0
    auto_login_page = 'login_form'
    unauth_page = ''
    logout_page = 'logged_out'

class _CookieCrumblerSetup(BaseRegistryTests):

    def _initSite(self, use_changed=False):

        self.root.site = DummySite()
        site = self.root.site
        site.cookie_authentication = DummyCookieCrumbler()
        cc = site.cookie_authentication
 
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

class CookieCrumblerConfiguratorTests(_CookieCrumblerSetup):

    def _getTargetClass(self):

        from Products.CMFSetup.cookieauth import CookieCrumblerConfigurator
        return CookieCrumblerConfigurator

    def test_generateXML_default( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )

        self._compareDOM( configurator.generateXML(), _DEFAULT_EXPORT )

    def test_generateXML_changed( self ):

        site = self._initSite(use_changed=True)
        configurator = self._makeOne( site ).__of__( site )

        self._compareDOM( configurator.generateXML(), _CHANGED_EXPORT )

    def test_parseXML_default( self ):

        site = self._initSite()
        configurator = self._makeOne(site)
        props = configurator.parseXML(_DEFAULT_EXPORT)

        self.assertEqual( props['auth_cookie'],'__ac')
        self.assertEqual( props['cache_header_value'],'private')
        self.assertEqual( props['name_cookie'],'__ac_name')
        self.assertEqual( props['log_username'],1)
        self.assertEqual( props['persist_cookie'],'__ac_persistent')
        self.assertEqual( props['pw_cookie'],'__ac_password')
        self.assertEqual( props['local_cookie_path'],0)
        self.assertEqual( props['auto_login_page'],'login_form')
        self.assertEqual( props['unauth_page'],'')
        self.assertEqual( props['logout_page'],'logged_out')

    def test_parseXML_changed( self ):

        site = self._initSite()
        configurator = self._makeOne(site)
        props = configurator.parseXML(_CHANGED_EXPORT)

        self.assertEqual( props['auth_cookie'],'value1')
        self.assertEqual( props['cache_header_value'],'value2')
        self.assertEqual( props['name_cookie'],'value3')
        self.assertEqual( props['log_username'],0)
        self.assertEqual( props['persist_cookie'],'value4')
        self.assertEqual( props['pw_cookie'],'value5')
        self.assertEqual( props['local_cookie_path'],1)
        self.assertEqual( props['auto_login_page'],'value6')
        self.assertEqual( props['unauth_page'],'value7')
        self.assertEqual( props['logout_page'],'value8')


class Test_importCookieCrumbler(_CookieCrumblerSetup):

    def test_normal(self):
        site = self._initSite()
        context = DummyImportContext(site)
        context._files['cookieauth.xml'] = _CHANGED_EXPORT

        from Products.CMFSetup.cookieauth import importCookieCrumbler
        importCookieCrumbler(context)

        cc = site.cookie_authentication
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

    def test_normal_encode_as_ascii(self):
        site = self._initSite()
        context = DummyImportContext(site, encoding='ascii')
        context._files['cookieauth.xml'] = _CHANGED_EXPORT

        from Products.CMFSetup.cookieauth import importCookieCrumbler
        importCookieCrumbler(context)

        cc = site.cookie_authentication
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


class Test_exportCookieCrumbler(_CookieCrumblerSetup):

    def test_unchanged(self):
        site = self._initSite( use_changed=False )
        context = DummyExportContext(site)

        from Products.CMFSetup.cookieauth import exportCookieCrumbler
        exportCookieCrumbler(context)

        self.assertEqual( len(context._wrote), 1 )
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'cookieauth.xml')
        self._compareDOM(text, _DEFAULT_EXPORT)
        self.assertEqual(content_type, 'text/xml')

    def test_changed(self):
        site = self._initSite( use_changed=True )
        context = DummyExportContext( site )

        from Products.CMFSetup.cookieauth import exportCookieCrumbler
        exportCookieCrumbler(context)

        self.assertEqual( len(context._wrote), 1 )
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'cookieauth.xml')
        self._compareDOM(text, _CHANGED_EXPORT)
        self.assertEqual(content_type, 'text/xml')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CookieCrumblerConfiguratorTests),
        unittest.makeSuite(Test_exportCookieCrumbler),
        unittest.makeSuite(Test_importCookieCrumbler),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
