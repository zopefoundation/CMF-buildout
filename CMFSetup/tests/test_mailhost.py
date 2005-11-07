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
"""Mailhost setup handler unit tests.

$Id$
"""

import unittest
import Testing

import Products
from OFS.Folder import Folder
from Products.Five import zcml
from Products.MailHost.MailHost import MailHost
from Products.CMFCore.tests.base.testcase import PlacelessSetup

from common import BaseRegistryTests
from common import DummyExportContext
from common import DummyImportContext


class _MailHostSetup(PlacelessSetup, BaseRegistryTests):

    def _initSite(self, use_changed=False):
        self.root.site = Folder(id='site')
        site = self.root.site
        mh = site.MailHost = MailHost('MailHost')
 
        if use_changed:
           mh.smtp_port='1'
           mh.smtp_pwd="value1"
           mh.smtp_host="value2"
           mh.smtp_uid="value3"

        return site

    def setUp(self):
        PlacelessSetup.setUp(self)
        BaseRegistryTests.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.GenericSetup.MailHost)

    def tearDown(self):
        BaseRegistryTests.tearDown(self)
        PlacelessSetup.tearDown(self)


_DEFAULT_EXPORT = """\
<?xml version="1.0"?>
<object name="MailHost" meta_type="Mail Host" smtp_host="localhost"
   smtp_port="25" smtp_pwd="" smtp_uid=""/>
"""

_CHANGED_EXPORT = """\
<?xml version="1.0"?>
<object name="MailHost" meta_type="Mail Host" smtp_host="value2"
   smtp_port="1" smtp_pwd="value1" smtp_uid="value3"/>
"""


class Test_exportMailHost(_MailHostSetup):

    def test_unchanged(self):
        from Products.CMFSetup.mailhost import exportMailHost

        site = self._initSite(use_changed=False)
        context = DummyExportContext(site)
        exportMailHost(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'mailhost.xml')
        self._compareDOM(text, _DEFAULT_EXPORT)
        self.assertEqual(content_type, 'text/xml')

    def test_changed(self):
        from Products.CMFSetup.mailhost import exportMailHost

        site = self._initSite(use_changed=True)
        context = DummyExportContext(site)
        exportMailHost(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'mailhost.xml')
        self._compareDOM(text, _CHANGED_EXPORT)
        self.assertEqual(content_type, 'text/xml')


class Test_importMailHost(_MailHostSetup):

    def test_normal(self):
        from Products.CMFSetup.mailhost import importMailHost

        site = self._initSite()
        mh = site.MailHost

        context = DummyImportContext(site)
        context._files['mailhost.xml'] = _CHANGED_EXPORT
        importMailHost(context)

        self.assertEqual( mh.smtp_pwd, 'value1' )
        self.assertEqual( mh.smtp_host, 'value2' )
        self.assertEqual( mh.smtp_uid, 'value3' )
        self.assertEqual( mh.smtp_port, 1 )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_exportMailHost),
        unittest.makeSuite(Test_importMailHost),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
