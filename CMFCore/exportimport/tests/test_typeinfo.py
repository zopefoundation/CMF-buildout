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
"""Types tool node adapter unit tests.

$Id$
"""

import unittest
import Testing
import Zope2
Zope2.startup()

from Products.CMFCore.tests.base.testcase import PlacelessSetup
from Products.GenericSetup.testing import NodeAdapterTestCase


_FTI_XML = """\
<object name="foo_fti" meta_type="Factory-based Type Information"
   xmlns:i18n="http://xml.zope.org/namespaces/i18n">
 <property name="title"></property>
 <property name="description"></property>
 <property name="content_icon"></property>
 <property name="content_meta_type"></property>
 <property name="product"></property>
 <property name="factory"></property>
 <property name="immediate_view"></property>
 <property name="global_allow">True</property>
 <property name="filter_content_types">True</property>
 <property name="allowed_content_types"/>
 <property name="allow_discussion">False</property>
 <alias from="(Default)" to="foo"/>
 <alias from="view" to="foo"/>
 <action title="Foo" action_id="foo_action" category="Bar"
    condition_expr="python:1" url_expr="string:${object_url}/foo"
    visible="True"/>
</object>
"""


class TypeInformationNodeAdapterTests(PlacelessSetup, NodeAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFCore.exportimport.typeinfo \
                import TypeInformationNodeAdapter

        return TypeInformationNodeAdapter

    def _populate(self, obj):
        obj.addAction('foo_action', 'Foo', 'string:${object_url}/foo',
                      'python:1', (), 'Bar')

    def _verifyImport(self, obj):
        self.assertEqual(type(obj._aliases), dict)
        self.assertEqual(obj._aliases, {'(Default)': 'foo', 'view': 'foo'})
        self.assertEqual(type(obj._aliases['view']), str)
        self.assertEqual(obj._aliases['view'], 'foo')
        self.assertEqual(type(obj._actions), tuple)
        self.assertEqual(type(obj._actions[0].id), str)
        self.assertEqual(obj._actions[0].id, 'foo_action')
        self.assertEqual(type(obj._actions[0].title), str)
        self.assertEqual(obj._actions[0].title, 'Foo')
        self.assertEqual(type(obj._actions[0].description), str)
        self.assertEqual(obj._actions[0].description, '')
        self.assertEqual(type(obj._actions[0].category), str)
        self.assertEqual(obj._actions[0].category, 'Bar')
        self.assertEqual(type(obj._actions[0].condition.text), str)
        self.assertEqual(obj._actions[0].condition.text, 'python:1')

    def setUp(self):
        from Products.CMFCore.TypesTool import FactoryTypeInformation
        import Products.CMFCore.exportimport
        import Products.Five
        from Products.Five import zcml

        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore.exportimport)

        self._obj = FactoryTypeInformation('foo_fti')
        self._XML = _FTI_XML


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TypeInformationNodeAdapterTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
