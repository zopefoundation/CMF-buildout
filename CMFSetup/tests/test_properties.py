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
""" Site properties export / import unit tests.

$Id$
"""

import unittest
import Testing

import Products
from Products.Five import zcml
from Products.CMFCore.PortalObject import PortalObjectBase
from Products.CMFCore.tests.base.testcase import PlacelessSetup

from common import BaseRegistryTests
from common import DummyExportContext
from common import DummyImportContext


_EMPTY_EXPORT = """\
<?xml version="1.0" ?>
<site>
 <property name="title"/>
</site>
"""

_NORMAL_EXPORT = """\
<?xml version="1.0" ?>
<site>
 <property name="title"/>
 <property name="foo" type="string">Foo</property>
 <property name="bar" type="tokens">
  <element value="Bar"/>
 </property>
 <property name="moo" type="tokens">
  <element value="Moo"/>
 </property>
</site>
"""


class _SitePropertiesSetup(PlacelessSetup, BaseRegistryTests):

    def _initSite(self, foo=2, bar=2):

        self.root.site = PortalObjectBase('foo_site')
        site = self.root.site

        if foo > 0:
            site._setProperty('foo', '', 'string')
        if foo > 1:
            site._updateProperty('foo', 'Foo')

        if bar > 0:
            site._setProperty( 'bar', (), 'tokens' )
            site._setProperty( 'moo', (), 'tokens' )
        if bar > 1:
            site._updateProperty( 'bar', ('Bar',) )
            site.moo = ['Moo']

        return site

    def setUp(self):
        PlacelessSetup.setUp(self)
        BaseRegistryTests.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore.exportimport)

    def tearDown(self):
        BaseRegistryTests.tearDown(self)
        PlacelessSetup.tearDown(self)


class Test_exportSiteProperties(_SitePropertiesSetup):

    def test_empty(self):
        from Products.CMFSetup.properties import exportSiteProperties

        site = self._initSite(0, 0)
        context = DummyExportContext(site)
        exportSiteProperties(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'properties.xml')
        self._compareDOM(text, _EMPTY_EXPORT)
        self.assertEqual(content_type, 'text/xml')

    def test_normal(self):
        from Products.CMFSetup.properties import exportSiteProperties

        site = self._initSite()
        context = DummyExportContext( site )
        exportSiteProperties(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'properties.xml')
        self._compareDOM(text, _NORMAL_EXPORT)
        self.assertEqual(content_type, 'text/xml')


class Test_importSiteProperties(_SitePropertiesSetup):

    def test_empty_default_purge(self):
        from Products.CMFSetup.properties import importSiteProperties

        site = self._initSite()

        self.assertEqual( len( site.propertyIds() ), 4 )
        self.failUnless( 'foo' in site.propertyIds() )
        self.assertEqual( site.getProperty('foo'), 'Foo' )
        self.failUnless( 'bar' in site.propertyIds() )
        self.assertEqual( site.getProperty('bar'), ('Bar',) )

        context = DummyImportContext(site)
        context._files['properties.xml'] = _EMPTY_EXPORT
        importSiteProperties(context)

        self.assertEqual( len( site.propertyIds() ), 1 )

    def test_empty_explicit_purge(self):
        from Products.CMFSetup.properties import importSiteProperties

        site = self._initSite()

        self.assertEqual( len( site.propertyIds() ), 4 )
        self.failUnless( 'foo' in site.propertyIds() )
        self.assertEqual( site.getProperty('foo'), 'Foo' )
        self.failUnless( 'bar' in site.propertyIds() )
        self.assertEqual( site.getProperty('bar'), ('Bar',) )

        context = DummyImportContext(site, True)
        context._files['properties.xml'] = _EMPTY_EXPORT
        importSiteProperties(context)

        self.assertEqual( len( site.propertyIds() ), 1 )

    def test_empty_skip_purge(self):
        from Products.CMFSetup.properties import importSiteProperties

        site = self._initSite()

        self.assertEqual( len( site.propertyIds() ), 4 )
        self.failUnless( 'foo' in site.propertyIds() )
        self.assertEqual( site.getProperty('foo'), 'Foo' )
        self.failUnless( 'bar' in site.propertyIds() )
        self.assertEqual( site.getProperty('bar'), ('Bar',) )

        context = DummyImportContext(site, False)
        context._files['properties.xml'] = _EMPTY_EXPORT
        importSiteProperties(context)

        self.assertEqual( len( site.propertyIds() ), 4 )
        self.failUnless( 'foo' in site.propertyIds() )
        self.assertEqual( site.getProperty('foo'), 'Foo' )
        self.failUnless( 'bar' in site.propertyIds() )
        self.assertEqual( site.getProperty('bar'), ('Bar',) )

    def test_normal(self):
        from Products.CMFSetup.properties import importSiteProperties

        site = self._initSite(0,0)

        self.assertEqual( len( site.propertyIds() ), 1 )

        context = DummyImportContext(site)
        context._files['properties.xml'] = _NORMAL_EXPORT
        importSiteProperties(context)

        self.assertEqual( len( site.propertyIds() ), 4 )
        self.failUnless( 'foo' in site.propertyIds() )
        self.assertEqual( site.getProperty('foo'), 'Foo' )
        self.failUnless( 'bar' in site.propertyIds() )
        self.assertEqual( site.getProperty('bar'), ('Bar',) )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_exportSiteProperties),
        unittest.makeSuite(Test_importSiteProperties),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
