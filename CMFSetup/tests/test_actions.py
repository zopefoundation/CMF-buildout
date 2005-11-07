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
""" CMFSetup action provider export / import unit tests

$Id$
"""

import unittest
import Testing
import Zope2
Zope2.startup()

import Products
from Acquisition import Implicit
from Acquisition import aq_parent
from OFS.Folder import Folder
from OFS.OrderedFolder import OrderedFolder
from Products.Five import zcml
from zope.interface import implements

from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.interfaces.portal_actions \
    import ActionProvider as IActionProvider
from Products.CMFCore.interfaces import IActionsTool
from Products.CMFCore.tests.base.testcase import PlacelessSetup

from common import BaseRegistryTests
from common import DummyExportContext
from common import DummyImportContext


class DummyTool( OrderedFolder, ActionProviderBase ):

    __implements__ = ( IActionProvider, )


class DummyUser( Implicit ):

    def getId( self ):
        return 'dummy'

class DummyMembershipTool( DummyTool ):

    def isAnonymousUser( self ):
        return False

    def getAuthenticatedMember( self ):
        return DummyUser().__of__( aq_parent( self ) )

class DummyActionsTool( DummyTool ):

    implements(IActionsTool)
    id = 'portal_actions'
    meta_type = 'CMF Actions Tool'

    def __init__( self ):

        self._providers = []

    def addActionProvider( self, provider_name ):

        self._providers.append( provider_name )

    def listActionProviders( self ):

        return self._providers[:]

    def deleteActionProvider( self, provider_name ):

        self._providers = [ x for x in self._providers if x != provider_name ]

class _ActionSetup(PlacelessSetup, BaseRegistryTests):

    def _initSite( self, foo=2, bar=2 ):
        self.root.site = Folder(id='site')
        site = self.root.site

        site.portal_membership = DummyMembershipTool()

        site.portal_actions = DummyActionsTool()
        site.portal_actions.addActionProvider( 'portal_actions' )

        if foo > 0:
            site.portal_foo = DummyTool()

        if foo > 1:
            site.portal_foo.addAction( id='foo'
                                    , name='Foo'
                                    , action='foo'
                                    , condition='python:1'
                                    , permission=()
                                    , category='dummy'
                                    , visible=1
                                    )
            site.portal_actions.addActionProvider( 'portal_foo' )

        if bar > 0:
            site.portal_bar = DummyTool()

        if bar > 1:
            site.portal_bar.addAction( id='bar'
                                    , name='Bar'
                                    , action='bar'
                                    , condition='python:0'
                                    , permission=( 'Manage portal', )
                                    , category='dummy'
                                    , visible=0
                                    )
            site.portal_actions.addActionProvider( 'portal_bar' )

        return site

    def setUp(self):
        PlacelessSetup.setUp(self)
        BaseRegistryTests.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore.exportimport)

    def tearDown(self):
        BaseRegistryTests.tearDown(self)
        PlacelessSetup.tearDown(self)

_EMPTY_EXPORT = """\
<?xml version="1.0"?>
<object meta_type="CMF Actions Tool" name="portal_actions" \
xmlns:i18n="http://xml.zope.org/namespaces/i18n">
 <action-provider name="portal_actions"/>
</object>
"""

_NORMAL_EXPORT = """\
<?xml version="1.0"?>
<object meta_type="CMF Actions Tool" name="portal_actions" \
xmlns:i18n="http://xml.zope.org/namespaces/i18n">
 <action-provider name="portal_actions"/>
 <action-provider name="portal_foo">
  <action action_id="foo"
          title="Foo"
          url_expr="string:${object_url}/foo"
          condition_expr="python:1"
          category="dummy"
          visible="True"/>
 </action-provider>
 <action-provider name="portal_bar">
  <action action_id="bar"
          title="Bar"
          url_expr="string:${object_url}/bar"
          condition_expr="python:0"
          category="dummy"
          visible="False">
   <permission>Manage portal</permission>
  </action>
 </action-provider>
</object>
"""

_NEWSYTLE_EXPORT = """\
<?xml version="1.0"?>
<object meta_type="CMF Actions Tool" name="portal_actions" \
xmlns:i18n="http://xml.zope.org/namespaces/i18n">
 <action-provider name="portal_actions"/>
 <object name="dummy" meta_type="CMF Action Category">
  <property name="title"></property>
  <object name="foo" meta_type="CMF Action">
   <property name="title">Foo</property>
   <property name="description"></property>
   <property name="url_expr">string:${object_url}/foo</property>
   <property name="icon_expr"></property>
   <property name="available_expr">python:1</property>
   <property name="permissions"></property>
   <property name="visible">True</property>
  </object>
  <object name="bar" meta_type="CMF Action">
   <property name="title">Bar</property>
   <property name="description"></property>
   <property name="url_expr">string:${object_url}/bar</property>
   <property name="icon_expr"></property>
   <property name="available_expr">python:0</property>
   <property name="permissions">
    <element value="Manage portal"/>
   </property>
   <property name="visible">False</property>
  </object>
 </object>
</object>
"""

_I18N_IMPORT = """\
<?xml version="1.0"?>
<object meta_type="CMF Actions Tool" name="portal_actions" \
xmlns:i18n="http://xml.zope.org/namespaces/i18n">
 <action-provider name="portal_actions"/>
 <object name="dummy" meta_type="CMF Action Category">
  <property name="title"></property>
  <object name="foo" meta_type="CMF Action" i18n:domain="foo_domain">
   <property name="title" i18n:translate="">Foo</property>
   <property name="description" i18n:translate=""></property>
   <property name="url_expr">string:${object_url}/foo</property>
   <property name="icon_expr"></property>
   <property name="available_expr">python:1</property>
   <property name="permissions"></property>
   <property name="visible">True</property>
  </object>
 </object>
</object>
"""

_INSERT_IMPORT = """\
<?xml version="1.0"?>
<actions-tool xmlns:i18n="http://xml.zope.org/namespaces/i18n">
 <object name="dummy">
 <object name="spam" meta_type="CMF Action" insert-before="*">
  <property name="title">Spam</property>
  <property name="description"></property>
  <property name="url_expr">string:${object_url}/spam</property>
  <property name="icon_expr">string:spam_icon.png</property>
  <property name="available_expr"></property>
  <property name="permissions">
   <element value="View" /></property>
  <property name="visible">True</property>
 </object>
 <object name="foo" insert-after="*">
  <property name="icon_expr">string:foo_icon.png</property>
 </object>
 </object>
</actions-tool>
"""

_REMOVE_IMPORT = """\
<?xml version="1.0"?>
<actions-tool xmlns:i18n="http://xml.zope.org/namespaces/i18n">
 <action-provider id="portal_actions" remove="">
 </action-provider>
 <action-provider id="not_existing" remove="">
 </action-provider>
 <action-provider id="portal_bar" remove="">
 </action-provider>
</actions-tool>
"""


class Test_exportActionProviders( _ActionSetup ):

    def test_unchanged( self ):

        site = self._initSite( 0, 0 )
        context = DummyExportContext( site )

        from Products.CMFSetup.actions import exportActionProviders
        exportActionProviders( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'actions.xml' )
        self._compareDOM( text, _EMPTY_EXPORT )
        self.assertEqual( content_type, 'text/xml' )

    def test_normal( self ):

        site = self._initSite()

        context = DummyExportContext( site )

        from Products.CMFSetup.actions import exportActionProviders
        exportActionProviders( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'actions.xml' )
        self._compareDOM( text, _NORMAL_EXPORT )
        self.assertEqual( content_type, 'text/xml' )


class Test_importActionProviders( _ActionSetup ):

    def test_empty_default_purge( self ):

        site = self._initSite( 2, 0 )
        atool = site.portal_actions

        self.assertEqual( len( atool.listActionProviders() ), 2 )
        self.failUnless( 'portal_foo' in atool.listActionProviders() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )

        context = DummyImportContext( site )
        context._files[ 'actions.xml' ] = _EMPTY_EXPORT

        from Products.CMFSetup.actions import importActionProviders
        importActionProviders( context )

        self.assertEqual( len( atool.listActionProviders() ), 1 )
        self.failIf( 'portal_foo' in atool.listActionProviders() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )
        self.assertEqual( len( atool.objectIds() ), 0 )

    def test_empty_explicit_purge( self ):

        site = self._initSite( 2, 0 )
        atool = site.portal_actions

        self.assertEqual( len( atool.listActionProviders() ), 2 )
        self.failUnless( 'portal_foo' in atool.listActionProviders() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )

        context = DummyImportContext( site, True )
        context._files[ 'actions.xml' ] = _EMPTY_EXPORT

        from Products.CMFSetup.actions import importActionProviders
        importActionProviders( context )

        self.assertEqual( len( atool.listActionProviders() ), 1 )
        self.failIf( 'portal_foo' in atool.listActionProviders() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )
        self.assertEqual( len( atool.objectIds() ), 0 )

    def test_empty_skip_purge( self ):

        site = self._initSite( 2, 0 )
        atool = site.portal_actions

        self.assertEqual( len( atool.listActionProviders() ), 2 )
        self.failUnless( 'portal_foo' in atool.listActionProviders() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )

        context = DummyImportContext( site, False )
        context._files[ 'actions.xml' ] = _EMPTY_EXPORT

        from Products.CMFSetup.actions import importActionProviders
        importActionProviders( context )

        self.assertEqual( len( atool.listActionProviders() ), 2 )
        self.failUnless( 'portal_foo' in atool.listActionProviders() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )

    def test_normal( self ):

        site = self._initSite( 1, 1 )
        atool = site.portal_actions
        foo = site.portal_foo
        bar = site.portal_bar

        self.assertEqual( len( atool.listActionProviders() ), 1 )
        self.failIf( 'portal_foo' in atool.listActionProviders() )
        self.failIf( foo.listActions() )
        self.failIf( 'portal_bar' in atool.listActionProviders() )
        self.failIf( bar.listActions() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )

        context = DummyImportContext( site )
        context._files[ 'actions.xml' ] = _NORMAL_EXPORT

        from Products.CMFSetup.actions import importActionProviders
        importActionProviders( context )

        self.assertEqual( len( atool.listActionProviders() ), 1 )
        self.failIf( 'portal_foo' in atool.listActionProviders() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )

        self.assertEqual( len( atool.objectIds() ), 1 )
        self.failUnless( 'dummy' in atool.objectIds() )
        self.assertEqual( len( atool.dummy.objectIds() ) , 2 )
        self.failUnless( 'foo' in atool.dummy.objectIds() )
        self.failUnless( 'bar' in atool.dummy.objectIds() )
        self.failIf( foo.listActions() )
        self.failIf( bar.listActions() )

        # complete the roundtrip
        context = DummyExportContext( site )
        from Products.CMFSetup.actions import exportActionProviders
        exportActionProviders( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'actions.xml' )
        self._compareDOM( text, _NEWSYTLE_EXPORT )
        self.assertEqual( content_type, 'text/xml' )

    def test_normal_encode_as_ascii( self ):

        site = self._initSite( 1, 1 )
        atool = site.portal_actions
        foo = site.portal_foo
        bar = site.portal_bar

        context = DummyImportContext( site, encoding='ascii' )
        context._files[ 'actions.xml' ] = _NORMAL_EXPORT

        from Products.CMFSetup.actions import importActionProviders
        importActionProviders( context )

        self.assertEqual( len( atool.listActionProviders() ), 1 )
        self.failIf( 'portal_foo' in atool.listActionProviders() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )

        self.assertEqual( len( atool.objectIds() ), 1 )
        self.failUnless( 'dummy' in atool.objectIds() )
        self.assertEqual( len( atool.dummy.objectIds() ), 2 )
        self.failUnless( 'foo' in atool.dummy.objectIds() )
        self.failUnless( 'bar' in atool.dummy.objectIds() )
        self.failIf( foo.listActions() )
        self.failIf( bar.listActions() )

    def test_i18n(self):

        from Products.CMFSetup.actions import importActionProviders

        site = self._initSite(0, 0)
        atool = site.portal_actions

        context = DummyImportContext(site)
        context._files['actions.xml'] = _I18N_IMPORT
        importActionProviders(context)

        self.assertEqual(len(atool.listActionProviders()), 1)
        self.assertEqual(atool.objectIds(), ['dummy'])
        self.assertEqual(atool.dummy.objectIds(), ['foo'])
        self.assertEqual(atool.dummy.foo.i18n_domain, 'foo_domain')

        # complete the roundtrip
        context = DummyExportContext(site)
        from Products.CMFSetup.actions import exportActionProviders
        exportActionProviders(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'actions.xml')
        self._compareDOM(text, _I18N_IMPORT)
        self.assertEqual(content_type, 'text/xml')

    def test_insert_skip_purge(self):

        from Products.CMFSetup.actions import importActionProviders

        site = self._initSite(0, 0)
        atool = site.portal_actions

        context = DummyImportContext(site)
        context._files['actions.xml'] = _NEWSYTLE_EXPORT
        importActionProviders(context)

        self.assertEqual( len( atool.listActionProviders() ), 1 )
        self.assertEqual( atool.objectIds(), ['dummy'] )
        self.assertEqual( atool.dummy.objectIds(), ['foo', 'bar'] )
        self.assertEqual( atool.dummy.foo.icon_expr, '' )

        context = DummyImportContext(site, False)
        context._files['actions.xml'] = _INSERT_IMPORT
        importActionProviders(context)

        self.assertEqual( len( atool.listActionProviders() ), 1 )
        self.assertEqual( atool.objectIds(), ['dummy'] )
        self.assertEqual( atool.dummy.objectIds(), ['spam', 'bar', 'foo'] )
        self.assertEqual( atool.dummy.foo.icon_expr, 'string:foo_icon.png' )

    def test_remove_skip_purge(self):

        from Products.CMFSetup.actions import importActionProviders

        site = self._initSite(2, 2)
        atool = site.portal_actions

        self.assertEqual( atool.listActionProviders(),
                          ['portal_actions', 'portal_foo', 'portal_bar'] )

        context = DummyImportContext(site, False)
        context._files['actions.xml'] = _REMOVE_IMPORT
        importActionProviders(context)

        self.assertEqual( atool.listActionProviders(), ['portal_foo'] )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( Test_exportActionProviders ),
        unittest.makeSuite( Test_importActionProviders ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
