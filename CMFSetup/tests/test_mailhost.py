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
""" MailHost properties export / import unit tests.

$Id$
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
<mailhost id="MailHost" smtp_pwd="" smtp_port="25"
          smtp_host="localhost.localdomain" i18n:domain="" smtp_uid=""
          xmlns:i18n="http://xml.zope.org/namespaces/i18n"/>
"""

_CHANGED_EXPORT = """\
<?xml version="1.0"?>
<mailhost id="MailHost" smtp_pwd="value1" smtp_port="1"
          smtp_host="value2" i18n:domain="" smtp_uid="value3"
          xmlns:i18n="http://xml.zope.org/namespaces/i18n"/>
"""

class DummySite(Folder):
    pass


class DummyMailHost:

    smtp_port='25'
    smtp_host="localhost.localdomain"
    smtp_uid=""
    smtp_pwd=""
    id='MailHost'

    def getId(self):
       return self.id

class _MailHostSetup(BaseRegistryTests):

    def _initSite(self, use_changed=False):

        self.root.site = DummySite()
        site = self.root.site
        site.MailHost = DummyMailHost()
        mh = site.MailHost
 
        if use_changed:
           mh.smtp_port='1'
           mh.smtp_pwd="value1"
           mh.smtp_host="value2"
           mh.smtp_uid="value3"


        return site

class MailHostConfiguratorTests(_MailHostSetup):

    def _getTargetClass(self):

        from Products.CMFSetup.mailhost import MailHostConfigurator
        return MailHostConfigurator

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

        self.assertEqual( props['smtp_port'],'25')
        self.assertEqual( props['smtp_host'],'localhost.localdomain')
        self.assertEqual( props['smtp_uid'],'')
        self.assertEqual( props['smtp_pwd'],'')

    def test_parseXML_changed( self ):

        site = self._initSite()
        configurator = self._makeOne(site)
        props = configurator.parseXML(_CHANGED_EXPORT)

        self.assertEqual( props['smtp_pwd'], 'value1' )
        self.assertEqual( props['smtp_host'], 'value2' )
        self.assertEqual( props['smtp_uid'], 'value3' )
        self.assertEqual( props['smtp_port'], '1' )


class Test_importMailHost(_MailHostSetup):

    def test_normal(self):
        site = self._initSite()
        context = DummyImportContext(site)
        context._files['mailhost.xml'] = _CHANGED_EXPORT

        from Products.CMFSetup.mailhost import importMailHost
        importMailHost(context)

        mh = site.MailHost
        self.assertEqual( mh.smtp_pwd, 'value1' )
        self.assertEqual( mh.smtp_host, 'value2' )
        self.assertEqual( mh.smtp_uid, 'value3' )
        self.assertEqual( mh.smtp_port, '1' )

    def test_normal_encode_as_ascii(self):
        site = self._initSite()
        context = DummyImportContext(site, encoding='ascii')
        context._files['mailhost.xml'] = _CHANGED_EXPORT

        from Products.CMFSetup.mailhost import importMailHost
        importMailHost(context)

        mh = site.MailHost
        self.assertEqual( mh.smtp_pwd, 'value1' )
        self.assertEqual( mh.smtp_host, 'value2' )
        self.assertEqual( mh.smtp_uid, 'value3' )
        self.assertEqual( mh.smtp_port, '1' )


class Test_exportMailHost(_MailHostSetup):

    def test_unchanged(self):
        site = self._initSite( use_changed=False )
        context = DummyExportContext(site)

        from Products.CMFSetup.mailhost import exportMailHost
        exportMailHost(context)

        self.assertEqual( len(context._wrote), 1 )
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'mailhost.xml')
        self._compareDOM(text, _DEFAULT_EXPORT)
        self.assertEqual(content_type, 'text/xml')

    def test_changed(self):
        site = self._initSite( use_changed=True )
        context = DummyExportContext( site )

        from Products.CMFSetup.mailhost import exportMailHost
        exportMailHost(context)

        self.assertEqual( len(context._wrote), 1 )
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'mailhost.xml')
        self._compareDOM(text, _CHANGED_EXPORT)
        self.assertEqual(content_type, 'text/xml')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(MailHostConfiguratorTests),
        unittest.makeSuite(Test_exportMailHost),
        unittest.makeSuite(Test_importMailHost),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
