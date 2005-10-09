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
import Zope2
Zope2.startup()

import Products
from Products.Five import zcml
from zope.app.tests.placelesssetup import PlacelessSetup

from Products.CMFCore.tests.base.dummy import DummySite
from Products.GenericSetup.testing import NodeAdapterTestCase


_ACTION_XML = """\
<object name="foo_action" meta_type="CMF Action">
 <property name="title">Foo</property>
 <property name="description"></property>
 <property name="url_expr">string:${object_url}/foo</property>
 <property name="icon_expr"></property>
 <property name="available_expr">python:1</property>
 <property name="permissions"/>
 <property name="visible">True</property>
</object>
"""

_ACTIONCATEGORY_XML = """\
<object name="foo_category" meta_type="CMF Action Category">
 <property name="title"></property>
 <object name="foo_action" meta_type="CMF Action">
  <property name="title"></property>
  <property name="description"></property>
  <property name="url_expr"></property>
  <property name="icon_expr"></property>
  <property name="available_expr"></property>
  <property name="permissions"/>
  <property name="visible">True</property>
 </object>
</object>
"""

_ACTIONSTOOL_XML = """\
<object name="portal_actions" meta_type="CMF Actions Tool"
   xmlns:i18n="http://xml.zope.org/namespaces/i18n">
 <action-provider name="portal_actions"/>
 <object name="foo_category" meta_type="CMF Action Category">
  <property name="title"></property>
  <object name="foo_action" meta_type="CMF Action" i18n:domain="foo_domain">
   <property name="title" i18n:translate=""></property>
   <property name="description" i18n:translate=""></property>
   <property name="url_expr"></property>
   <property name="icon_expr"></property>
   <property name="available_expr"></property>
   <property name="permissions"/>
   <property name="visible">True</property>
  </object>
 </object>
</object>
"""

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


class ActionNodeAdapterTests(PlacelessSetup, NodeAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFCore.nodeadapters import ActionNodeAdapter

        return ActionNodeAdapter

    def _populate(self, obj):
        obj._setPropValue('title', 'Foo')
        obj._setPropValue('url_expr', 'string:${object_url}/foo')
        obj._setPropValue('available_expr', 'python:1')

    def setUp(self):
        from Products.CMFCore.ActionInformation import Action

        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore)

        self._obj = Action('foo_action')
        self._XML = _ACTION_XML


class ActionCategoryNodeAdapterTests(PlacelessSetup, NodeAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFCore.nodeadapters import ActionCategoryNodeAdapter

        return ActionCategoryNodeAdapter

    def _populate(self, obj):
        from Products.CMFCore.ActionInformation import Action

        obj._setObject('foo_action', Action('foo_action'))

    def setUp(self):
        from Products.CMFCore.ActionInformation import ActionCategory

        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore)

        self._obj = ActionCategory('foo_category')
        self._XML = _ACTIONCATEGORY_XML


class ActionsToolNodeAdapterTests(PlacelessSetup, NodeAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFCore.nodeadapters import ActionsToolNodeAdapter

        return ActionsToolNodeAdapter

    def _populate(self, obj):
        from Products.CMFCore.ActionInformation import Action
        from Products.CMFCore.ActionInformation import ActionCategory

        obj._setObject('foo_category', ActionCategory('foo_category'))
        obj.action_providers = ('portal_actions',)
        obj.foo_category._setObject('foo_action', Action('foo_action'))
        obj.foo_category.foo_action.i18n_domain = 'foo_domain'

    def setUp(self):
        from Products.CMFCore.ActionsTool import ActionsTool

        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore)

        site = DummySite('site')
        site._setObject('portal_actions', ActionsTool('portal_actions'))
        self._obj = site.portal_actions
        self._XML = _ACTIONSTOOL_XML


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
        unittest.makeSuite(ActionNodeAdapterTests),
        unittest.makeSuite(ActionCategoryNodeAdapterTests),
        unittest.makeSuite(ActionsToolNodeAdapterTests),
        unittest.makeSuite(CookieCrumblerNodeAdapterTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
