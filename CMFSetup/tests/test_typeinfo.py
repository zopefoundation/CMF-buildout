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
"""Types tool setup handler unit tests.

$Id$
"""

import unittest
import Testing
import Zope2
Zope2.startup()

import Products
from OFS.Folder import Folder
from Products.Five import zcml
from zope.app.tests.placelesssetup import PlacelessSetup

from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.TypesTool import ScriptableTypeInformation
from Products.CMFCore.TypesTool import TypesTool

from common import BaseRegistryTests
from common import DummyExportContext
from common import DummyImportContext


class _TypeInfoSetup(PlacelessSetup, BaseRegistryTests):

    def _initSite(self, foo=0):
        self.root.site = Folder(id='site')
        site = self.root.site
        ttool = site.portal_types = TypesTool()

        if foo == 1:
            fti = _TI_LIST[0].copy()
            ttool._setObject(fti['id'], FactoryTypeInformation(**fti))
            sti = _TI_LIST[1].copy()
            ttool._setObject(sti['id'], ScriptableTypeInformation(**sti))
        elif foo == 2:
            fti = _TI_LIST_WITH_FILENAME[0].copy()
            ttool._setObject(fti['id'], FactoryTypeInformation(**fti))
            sti = _TI_LIST_WITH_FILENAME[1].copy()
            ttool._setObject(sti['id'], ScriptableTypeInformation(**sti))

        return site

    def setUp(self):
        PlacelessSetup.setUp(self)
        BaseRegistryTests.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore)

    def tearDown(self):
        BaseRegistryTests.tearDown(self)
        PlacelessSetup.tearDown(self)


class TypesToolExportConfiguratorTests(_TypeInfoSetup):

    def _getTargetClass(self):

        from Products.CMFSetup.typeinfo import TypesToolExportConfigurator
        return TypesToolExportConfigurator

    def test_listTypeInfo_empty(self):

        site = self._initSite()
        configurator = self._makeOne(site).__of__(site)

        self.assertEqual(len(configurator.listTypeInfo()), 0)

    def test_listTypeInfo_filled(self):

        site = self._initSite(1)
        configurator = self._makeOne(site).__of__(site)

        self.assertEqual(len(configurator.listTypeInfo()), len(_TI_LIST))

        info_list = configurator.listTypeInfo()
        self.assertEqual(len(info_list), len(_TI_LIST))

        _marker = object()

        for i in range(len(_TI_LIST)):
            found = info_list[i]
            expected = _TI_LIST[1-i]
            self.assertEqual(found['id'], expected['id'])
            self.failUnless(found.get('filename', _marker) is _marker)

    def test_listTypeInfo_with_filename (self):

        site = self._initSite(2)
        configurator = self._makeOne(site).__of__(site)

        info_list = configurator.listTypeInfo()
        self.assertEqual(len(info_list), len(_TI_LIST_WITH_FILENAME))

        for i in range(len(_TI_LIST_WITH_FILENAME)):
            found = info_list[i]
            expected = _TI_LIST_WITH_FILENAME[1-i]
            self.assertEqual(found['id'], expected['id'])
            self.assertEqual(found['filename'],
                             'types/%s.xml'
                             % expected['id'].replace(' ', '_')
                             )

    def test_generateXML_empty(self):

        site = self._initSite()
        configurator = self._makeOne(site).__of__(site)
        self._compareDOM(configurator.generateXML(), _EMPTY_TOOL_EXPORT)

    def test_generateXML_normal(self):

        site = self._initSite(1)
        configurator = self._makeOne(site).__of__(site)
        self._compareDOM(configurator.generateXML(), _NORMAL_TOOL_EXPORT)

    def test_generateXML_explicit_filename(self):

        site = self._initSite(2)
        configurator = self._makeOne(site).__of__(site)
        self._compareDOM(configurator.generateXML(), _FILENAME_EXPORT)


class TypesToolImportConfiguratorTests(_TypeInfoSetup):

    def _getTargetClass(self):

        from Products.CMFSetup.typeinfo import TypesToolImportConfigurator
        return TypesToolImportConfigurator

    def test_parseXML_empty(self):

        site = self._initSite()
        configurator = self._makeOne(site).__of__(site)

        tool_info = configurator.parseXML(_EMPTY_TOOL_EXPORT)
        self.assertEqual(len(tool_info['types']), 0)

    def test_parseXML_normal(self):

        site = self._initSite()
        configurator = self._makeOne(site).__of__(site)

        tool_info = configurator.parseXML(_NORMAL_TOOL_EXPORT)
        self.assertEqual(len(tool_info['types']), 2)

        type_info = tool_info['types'][1]
        self.assertEqual(type_info['id'], 'foo')
        self.assertEqual(type_info['filename'], 'types/foo.xml')
        type_info = tool_info['types'][0]
        self.assertEqual(type_info['id'], 'bar')
        self.assertEqual(type_info['filename'], 'types/bar.xml')

    def test_parseXML_with_filename(self):

        site = self._initSite()
        configurator = self._makeOne(site).__of__(site)

        tool_info = configurator.parseXML(_FILENAME_EXPORT)
        self.assertEqual(len(tool_info['types']), 2)

        type_info = tool_info['types'][1]
        self.assertEqual(type_info['id'], 'foo object')
        self.assertEqual(type_info['filename'], 'types/foo_object.xml')
        type_info = tool_info['types'][0]
        self.assertEqual(type_info['id'], 'bar object')
        self.assertEqual(type_info['filename'], 'types/bar_object.xml')


_TI_LIST = ({
    'id':                    'foo',
    'title':                 'Foo',
    'description':           'Foo things',
    'i18n_domain':           'foo_domain',
    'content_meta_type':     'Foo Thing',
    'content_icon':          'foo.png',
    'product':               'CMFSetup',
    'factory':               'addFoo',
    'immediate_view':        'foo_view',
    'filter_content_types':  False,
    'allowed_content_types': (),
    'allow_discussion':      False,
    'global_allow':          False,
    'aliases': {'(Default)': 'foo_view',
                'view':      'foo_view',
                },
    'actions': ({'id':     'view',
                 'name':   'View',
                 'action': 'string:${object_url}/foo_view',
                 'permissions': (View,),
                 },
                {'id':     'edit',
                 'name':   'Edit',
                 'action': 'string:${object_url}/foo_edit_form',
                 'permissions': (ModifyPortalContent,),
                 },
                {'id':     'metadata',
                 'name':   'Metadata',
                 'action': 'string:${object_url}/metadata_edit_form',
                 'permissions': (ModifyPortalContent,),
                 },
                ),
    }, {
    'id':                    'bar',
    'title':                 'Bar',
    'description':           'Bar things',
    'content_meta_type':     'Bar Thing',
    'content_icon':          'bar.png',
    'constructor_path':      'make_bar',
    'permission':            'Add portal content',
    'immediate_view':        'bar_view',
    'filter_content_types':  True,
    'allowed_content_types': ('foo',),
    'allow_discussion':      True,
    'global_allow':          True,
    'aliases': {'(Default)': 'bar_view',
                'view':      'bar_view',
                },
    'actions': ({'id':     'view',
                 'name':   'View',
                 'action': 'string:${object_url}/bar_view',
                 'permissions': (View,),
                 },
                {'id':     'edit',
                 'name':   'Edit',
                 'action': 'string:${object_url}/bar_edit_form',
                 'permissions': (ModifyPortalContent,),
                 },
                {'id':     'contents',
                 'name':   'Contents',
                 'action': 'string:${object_url}/folder_contents',
                 'permissions': (AccessContentsInformation,),
                 },
                {'id':     'metadata',
                 'name':   'Metadata',
                 'action': 'string:${object_url}/metadata_edit_form',
                 'permissions': (ModifyPortalContent,),
                 },
               ),
    })

_TI_LIST_WITH_FILENAME = []

for original in _TI_LIST:
    duplicate = original.copy()
    duplicate['id'] = '%s object' % original['id']
    _TI_LIST_WITH_FILENAME.append(duplicate)

_EMPTY_TOOL_EXPORT = """\
<?xml version="1.0"?>
<types-tool>
</types-tool>
"""

_NORMAL_TOOL_EXPORT = """\
<?xml version="1.0"?>
<types-tool>
 <type id="bar" />
 <type id="foo" />
</types-tool>
"""

_FILENAME_EXPORT = """\
<?xml version="1.0"?>
<types-tool>
 <type id="bar object" filename="types/bar_object.xml" />
 <type id="foo object" filename="types/foo_object.xml" />
</types-tool>
"""

_UPDATE_TOOL_IMPORT = """\
<?xml version="1.0"?>
<types-tool>
 <type id="foo"/>
</types-tool>
"""

_FOO_OLD_EXPORT = """\
<?xml version="1.0"?>
<type-info
   id="%s"
   kind="Factory-based Type Information"
   title="Foo"
   meta_type="Foo Thing"
   icon="foo.png"
   product="CMFSetup"
   factory="addFoo"
   immediate_view="foo_view"
   filter_content_types="False"
   allow_discussion="False"
   global_allow="False" >
  <description>Foo things</description>
  <aliases>
   <alias from="(Default)" to="foo_view" />
   <alias from="view" to="foo_view" />
  </aliases>
  <action
     action_id="view"
     title="View"
     url_expr="string:${object_url}/foo_view"
     condition_expr=""
     category="object"
     visible="True">
   <permission>View</permission>
  </action>
  <action
     action_id="edit"
     title="Edit"
     url_expr="string:${object_url}/foo_edit_form"
     condition_expr=""
     category="object"
     visible="True">
   <permission>Modify portal content</permission>
  </action>
  <action
     action_id="metadata"
     title="Metadata"
     url_expr="string:${object_url}/metadata_edit_form"
     condition_expr=""
     category="object"
     visible="True">
   <permission>Modify portal content</permission>
  </action>
</type-info>
"""

_FOO_EXPORT = """\
<?xml version="1.0"?>
<object name="%s" meta_type="Factory-based Type Information"
   i18n:domain="foo_domain" xmlns:i18n="http://xml.zope.org/namespaces/i18n">
 <property name="title" i18n:translate="">Foo</property>
 <property name="description" i18n:translate="">Foo things</property>
 <property name="content_icon">foo.png</property>
 <property name="content_meta_type">Foo Thing</property>
 <property name="product">CMFSetup</property>
 <property name="factory">addFoo</property>
 <property name="immediate_view">foo_view</property>
 <property name="global_allow">False</property>
 <property name="filter_content_types">False</property>
 <property name="allowed_content_types"/>
 <property name="allow_discussion">False</property>
 <alias from="(Default)" to="foo_view"/>
 <alias from="view" to="foo_view"/>
 <action title="View" action_id="view" category="object" condition_expr=""
    url_expr="string:${object_url}/foo_view" visible="True">
  <permission value="View"/>
 </action>
 <action title="Edit" action_id="edit" category="object" condition_expr=""
    url_expr="string:${object_url}/foo_edit_form" visible="True">
  <permission value="Modify portal content"/>
 </action>
 <action title="Metadata" action_id="metadata" category="object"
    condition_expr="" url_expr="string:${object_url}/metadata_edit_form"
    visible="True">
  <permission value="Modify portal content"/>
 </action>
</object>
"""

_BAR_OLD_EXPORT = """\
<?xml version="1.0"?>
<type-info
   id="%s"
   kind="Scriptable Type Information"
   title="Bar"
   meta_type="Bar Thing"
   icon="bar.png"
   constructor_path="make_bar"
   permission="Add portal content"
   immediate_view="bar_view"
   filter_content_types="True"
   allow_discussion="True"
   global_allow="True" >
  <description>Bar things</description>
  <allowed_content_type>foo</allowed_content_type>
  <aliases>
   <alias from="(Default)" to="bar_view" />
   <alias from="view" to="bar_view" />
  </aliases>
  <action
     action_id="view"
     title="View"
     url_expr="string:${object_url}/bar_view"
     condition_expr=""
     category="object"
     visible="True">
   <permission>View</permission>
  </action>
  <action
     action_id="edit"
     title="Edit"
     url_expr="string:${object_url}/bar_edit_form"
     condition_expr=""
     category="object"
     visible="True">
   <permission>Modify portal content</permission>
  </action>
  <action
     action_id="contents"
     title="Contents"
     url_expr="string:${object_url}/folder_contents"
     condition_expr=""
     category="object"
     visible="True">
   <permission>Access contents information</permission>
  </action>
  <action
     action_id="metadata"
     title="Metadata"
     url_expr="string:${object_url}/metadata_edit_form"
     condition_expr=""
     category="object"
     visible="True">
   <permission>Modify portal content</permission>
  </action>
</type-info>
"""

_BAR_EXPORT = """\
<?xml version="1.0"?>
<object name="%s" meta_type="Scriptable Type Information"
   xmlns:i18n="http://xml.zope.org/namespaces/i18n">
 <property name="title">Bar</property>
 <property name="description">Bar things</property>
 <property name="content_icon">bar.png</property>
 <property name="content_meta_type">Bar Thing</property>
 <property name="permission">Add portal content</property>
 <property name="constructor_path">make_bar</property>
 <property name="immediate_view">bar_view</property>
 <property name="global_allow">True</property>
 <property name="filter_content_types">True</property>
 <property name="allowed_content_types">
  <element value="foo"/>
 </property>
 <property name="allow_discussion">True</property>
 <alias from="(Default)" to="bar_view"/>
 <alias from="view" to="bar_view"/>
 <action title="View" action_id="view" category="object" condition_expr=""
    url_expr="string:${object_url}/bar_view" visible="True">
  <permission value="View"/>
 </action>
 <action title="Edit" action_id="edit" category="object" condition_expr=""
    url_expr="string:${object_url}/bar_edit_form" visible="True">
  <permission value="Modify portal content"/>
 </action>
 <action title="Contents" action_id="contents" category="object"
    condition_expr="" url_expr="string:${object_url}/folder_contents"
    visible="True">
  <permission value="Access contents information"/>
 </action>
 <action title="Metadata" action_id="metadata" category="object"
    condition_expr="" url_expr="string:${object_url}/metadata_edit_form"
    visible="True">
  <permission value="Modify portal content"/>
 </action>
</object>
"""

_UPDATE_FOO_IMPORT = """\
<object name="foo">
 <alias from="spam" to="eggs"/>
</object>
"""


class Test_exportTypesTool(_TypeInfoSetup):

    def test_empty(self):
        from Products.CMFSetup.typeinfo import exportTypesTool

        site = self._initSite()
        context = DummyExportContext(site)
        exportTypesTool(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'typestool.xml')
        self._compareDOM(text, _EMPTY_TOOL_EXPORT)
        self.assertEqual(content_type, 'text/xml')

    def test_normal(self):
        from Products.CMFSetup.typeinfo import exportTypesTool

        site = self._initSite(1)
        context = DummyExportContext(site)
        exportTypesTool(context)

        self.assertEqual(len(context._wrote), 3)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'typestool.xml')
        self._compareDOM(text, _NORMAL_TOOL_EXPORT)
        self.assertEqual(content_type, 'text/xml')

        filename, text, content_type = context._wrote[1]
        self.assertEqual(filename, 'types/bar.xml')
        self._compareDOM(text, _BAR_EXPORT % 'bar')
        self.assertEqual(content_type, 'text/xml')

        filename, text, content_type = context._wrote[2]
        self.assertEqual(filename, 'types/foo.xml')
        self._compareDOM(text, _FOO_EXPORT % 'foo')
        self.assertEqual(content_type, 'text/xml')

    def test_with_filenames(self):
        from Products.CMFSetup.typeinfo import exportTypesTool

        site = self._initSite(2)
        context = DummyExportContext(site)
        exportTypesTool(context)

        self.assertEqual(len(context._wrote), 3)

        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'typestool.xml')
        self._compareDOM(text, _FILENAME_EXPORT)
        self.assertEqual(content_type, 'text/xml')

        filename, text, content_type = context._wrote[1]
        self.assertEqual(filename, 'types/bar_object.xml')
        self._compareDOM(text, _BAR_EXPORT % 'bar object')
        self.assertEqual(content_type, 'text/xml')

        filename, text, content_type = context._wrote[2]
        self.assertEqual(filename, 'types/foo_object.xml')
        self._compareDOM(text, _FOO_EXPORT % 'foo object')
        self.assertEqual(content_type, 'text/xml')

class Test_importTypesTool(_TypeInfoSetup):

    def test_empty_default_purge(self):
        from Products.CMFSetup.typeinfo import importTypesTool

        site = self._initSite(1)
        tool = site.portal_types

        self.assertEqual(len(tool.objectIds()), 2)

        context = DummyImportContext(site)
        context._files['typestool.xml'] = _EMPTY_TOOL_EXPORT
        importTypesTool(context)

        self.assertEqual(len(tool.objectIds()), 0)

    def test_empty_explicit_purge(self):
        from Products.CMFSetup.typeinfo import importTypesTool

        site = self._initSite(1)
        tool = site.portal_types

        self.assertEqual(len(tool.objectIds()), 2)

        context = DummyImportContext(site, True)
        context._files['typestool.xml'] = _EMPTY_TOOL_EXPORT
        importTypesTool(context)

        self.assertEqual(len(tool.objectIds()), 0)

    def test_empty_skip_purge(self):
        from Products.CMFSetup.typeinfo import importTypesTool

        site = self._initSite(1)
        tool = site.portal_types

        self.assertEqual(len(tool.objectIds()), 2)

        context = DummyImportContext(site, False)
        context._files['typestool.xml'] = _EMPTY_TOOL_EXPORT
        importTypesTool(context)

        self.assertEqual(len(tool.objectIds()), 2)

    def test_normal(self):
        from Products.CMFSetup.typeinfo import importTypesTool

        site = self._initSite()
        tool = site.portal_types

        self.assertEqual(len(tool.objectIds()), 0)

        context = DummyImportContext(site)
        context._files['typestool.xml'] = _NORMAL_TOOL_EXPORT
        context._files['types/foo.xml'] = _FOO_EXPORT % 'foo'
        context._files['types/bar.xml'] = _BAR_EXPORT % 'bar'
        importTypesTool(context)

        self.assertEqual(len(tool.objectIds()), 2)
        self.failUnless('foo' in tool.objectIds())
        self.failUnless('bar' in tool.objectIds())

    def test_old_xml(self):
        from Products.CMFSetup.typeinfo import exportTypesTool
        from Products.CMFSetup.typeinfo import importTypesTool

        site = self._initSite()
        tool = site.portal_types

        self.assertEqual(len(tool.objectIds()), 0)

        context = DummyImportContext(site)
        context._files['typestool.xml'] = _NORMAL_TOOL_EXPORT
        context._files['types/foo.xml'] = _FOO_OLD_EXPORT % 'foo'
        context._files['types/bar.xml'] = _BAR_OLD_EXPORT % 'bar'
        importTypesTool(context)

        self.assertEqual(len(tool.objectIds()), 2)
        self.failUnless('foo' in tool.objectIds())
        self.failUnless('bar' in tool.objectIds())

        context = DummyExportContext(site)
        exportTypesTool(context)

        filename, text, content_type = context._wrote[1]
        self.assertEqual(filename, 'types/bar.xml')
        self._compareDOM(text, _BAR_EXPORT % 'bar')
        self.assertEqual(content_type, 'text/xml')

    def test_with_filenames(self):
        from Products.CMFSetup.typeinfo import importTypesTool

        site = self._initSite()
        tool = site.portal_types

        self.assertEqual(len(tool.objectIds()), 0)

        context = DummyImportContext(site)
        context._files['typestool.xml'] = _FILENAME_EXPORT
        context._files['types/foo_object.xml'] = _FOO_EXPORT % 'foo object'
        context._files['types/bar_object.xml'] = _BAR_EXPORT % 'bar object'
        importTypesTool(context)

        self.assertEqual(len(tool.objectIds()), 2)
        self.failUnless('foo object' in tool.objectIds())
        self.failUnless('bar object' in tool.objectIds())

    def test_normal_update(self):
        from Products.CMFSetup.typeinfo import importTypesTool

        site = self._initSite()
        tool = site.portal_types

        context = DummyImportContext(site)
        context._files['typestool.xml'] = _NORMAL_TOOL_EXPORT
        context._files['types/foo.xml'] = _FOO_EXPORT % 'foo'
        context._files['types/bar.xml'] = _BAR_EXPORT % 'bar'
        importTypesTool(context)

        self.assertEqual(tool.foo.title, 'Foo')
        self.assertEqual(tool.foo.content_meta_type, 'Foo Thing')
        self.assertEqual(tool.foo.content_icon, 'foo.png')
        self.assertEqual(tool.foo.immediate_view, 'foo_view')
        self.assertEqual(tool.foo._aliases,
                         {'(Default)': 'foo_view', 'view': 'foo_view'})

        context = DummyImportContext(site, False)
        context._files['typestool.xml'] = _UPDATE_TOOL_IMPORT
        context._files['types/foo.xml'] = _UPDATE_FOO_IMPORT
        importTypesTool(context)

        self.assertEqual(tool.foo.title, 'Foo')
        self.assertEqual(tool.foo.content_meta_type, 'Foo Thing')
        self.assertEqual(tool.foo.content_icon, 'foo.png')
        self.assertEqual(tool.foo.immediate_view, 'foo_view')
        self.assertEqual(tool.foo._aliases,
               {'(Default)': 'foo_view', 'view': 'foo_view', 'spam': 'eggs'})


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TypesToolExportConfiguratorTests),
        unittest.makeSuite(TypesToolImportConfiguratorTests),
        unittest.makeSuite(Test_exportTypesTool),
        unittest.makeSuite(Test_importTypesTool),
       ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
