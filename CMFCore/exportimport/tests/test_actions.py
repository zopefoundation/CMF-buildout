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
"""Actions tool node adapter unit tests.

$Id$
"""

import unittest
import Testing
import Zope2
Zope2.startup()

from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.testcase import PlacelessSetup
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


class ActionNodeAdapterTests(PlacelessSetup, NodeAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFCore.exportimport.actions import ActionNodeAdapter

        return ActionNodeAdapter

    def _populate(self, obj):
        obj._setPropValue('title', 'Foo')
        obj._setPropValue('url_expr', 'string:${object_url}/foo')
        obj._setPropValue('available_expr', 'python:1')

    def _verifyImport(self, obj):
        self.assertEqual(type(obj.title), str)
        self.assertEqual(obj.title, 'Foo')
        self.assertEqual(type(obj.description), str)
        self.assertEqual(obj.description, '')
        self.assertEqual(type(obj.url_expr), str)
        self.assertEqual(obj.url_expr, 'string:${object_url}/foo')
        self.assertEqual(type(obj.icon_expr), str)
        self.assertEqual(obj.icon_expr, '')
        self.assertEqual(type(obj.available_expr), str)
        self.assertEqual(obj.available_expr, 'python:1')
        self.assertEqual(type(obj.permissions), tuple)
        self.assertEqual(obj.permissions, ())
        self.assertEqual(type(obj.visible), bool)
        self.assertEqual(obj.visible, True)

    def setUp(self):
        from Products.CMFCore.ActionInformation import Action
        import Products.CMFCore.exportimport
        import Products.Five
        from Products.Five import zcml

        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore.exportimport)

        self._obj = Action('foo_action')
        self._XML = _ACTION_XML


class ActionCategoryNodeAdapterTests(PlacelessSetup, NodeAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFCore.exportimport.actions \
                import ActionCategoryNodeAdapter

        return ActionCategoryNodeAdapter

    def _populate(self, obj):
        from Products.CMFCore.ActionInformation import Action

        obj._setObject('foo_action', Action('foo_action'))

    def _verifyImport(self, obj):
        self.assertEqual(type(obj.title), str)
        self.assertEqual(obj.title, '')

    def setUp(self):
        from Products.CMFCore.ActionInformation import ActionCategory
        import Products.CMFCore.exportimport
        import Products.Five
        from Products.Five import zcml

        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore.exportimport)

        self._obj = ActionCategory('foo_category')
        self._XML = _ACTIONCATEGORY_XML


class ActionsToolNodeAdapterTests(PlacelessSetup, NodeAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFCore.exportimport.actions \
                import ActionsToolNodeAdapter

        return ActionsToolNodeAdapter

    def _populate(self, obj):
        from Products.CMFCore.ActionInformation import Action
        from Products.CMFCore.ActionInformation import ActionCategory

        obj._setObject('foo_category', ActionCategory('foo_category'))
        obj.action_providers = ('portal_actions',)
        obj.foo_category._setObject('foo_action', Action('foo_action'))
        obj.foo_category.foo_action.i18n_domain = 'foo_domain'

    def _verifyImport(self, obj):
        self.assertEqual(type(obj.action_providers), tuple)
        self.assertEqual(obj.action_providers, ('portal_actions',))
        self.assertEqual(type(obj.action_providers[0]), str)
        self.assertEqual(obj.action_providers[0], 'portal_actions')

    def setUp(self):
        from Products.CMFCore.ActionsTool import ActionsTool
        import Products.CMFCore.exportimport
        import Products.Five
        from Products.Five import zcml

        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore.exportimport)

        site = DummySite('site')
        site._setObject('portal_actions', ActionsTool('portal_actions'))
        self._obj = site.portal_actions
        self._XML = _ACTIONSTOOL_XML


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ActionNodeAdapterTests),
        unittest.makeSuite(ActionCategoryNodeAdapterTests),
        unittest.makeSuite(ActionsToolNodeAdapterTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
