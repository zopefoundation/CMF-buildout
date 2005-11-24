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
"""ContentTypeRegistry setup handler unit tests.

$Id$
"""

import unittest
import Testing

import Products
from Products.Five import zcml

from Products.CMFCore.tests.base.testcase import PlacelessSetup
from Products.GenericSetup.tests.common import BaseRegistryTests
from Products.GenericSetup.tests.common import DummyExportContext
from Products.GenericSetup.tests.common import DummyImportContext

_TEST_PREDICATES = (
 ('plain_text', 'major_minor', ('text', 'plain,javascript'), 'File'),
 ('stylesheets', 'extension', ('css,xsl,xslt',), 'Text File'),
 ('images', 'mimetype_regex', ('image/.*',), 'Image'),
 ('logfiles', 'name_regex', ('error_log-.*',), 'Log File'),
)

class _ContentTypeRegistrySetup(PlacelessSetup, BaseRegistryTests):

    MAJOR_MINOR_ID = _TEST_PREDICATES[0][0]
    MAJOR = _TEST_PREDICATES[0][2][0]
    MINOR = _TEST_PREDICATES[0][2][1]
    MAJOR_MINOR_TYPENAME = _TEST_PREDICATES[0][3]
    EXTENSION_ID = _TEST_PREDICATES[1][0]
    EXTENSIONS = _TEST_PREDICATES[1][2][0]
    EXTENSION_TYPENAME = _TEST_PREDICATES[1][3]
    MIMETYPE_REGEX_ID = _TEST_PREDICATES[2][0]
    MIMETYPE_REGEX = _TEST_PREDICATES[2][2][0]
    MIMETYPE_REGEX_TYPENAME = _TEST_PREDICATES[2][3]
    NAME_REGEX_ID = _TEST_PREDICATES[3][0]
    NAME_REGEX = _TEST_PREDICATES[3][2][0]
    NAME_REGEX_TYPENAME = _TEST_PREDICATES[3][3]

    _EMPTY_EXPORT = """\
<?xml version="1.0"?>
<object name="content_type_registry" meta_type="Content Type Registry"/>
"""

    _WITH_POLICY_EXPORT = """\
<?xml version="1.0"?>
<object name="content_type_registry" meta_type="Content Type Registry">
 <predicate name="%s" content_type_name="%s"
    predicate_type="major_minor">
  <argument value="%s"/>
  <argument value="%s"/>
 </predicate>
 <predicate name="%s" content_type_name="%s"
    predicate_type="extension">
  <argument value="%s"/>
 </predicate>
 <predicate name="%s" content_type_name="%s"
    predicate_type="mimetype_regex">
  <argument value="%s"/>
 </predicate>
 <predicate name="%s" content_type_name="%s"
    predicate_type="name_regex">
  <argument value="%s"/>
 </predicate>
</object>
""" % (MAJOR_MINOR_ID,
       MAJOR_MINOR_TYPENAME,
       MAJOR,
       MINOR,
       EXTENSION_ID,
       EXTENSION_TYPENAME,
       EXTENSIONS,
       MIMETYPE_REGEX_ID,
       MIMETYPE_REGEX_TYPENAME,
       MIMETYPE_REGEX,
       NAME_REGEX_ID,
       NAME_REGEX_TYPENAME,
       NAME_REGEX,
      )

    def _initSite(self, mit_predikat=False):
        from OFS.Folder import Folder
        from Products.CMFCore.ContentTypeRegistry import ContentTypeRegistry

        self.root.site = Folder(id='site')
        site = self.root.site
        ctr = ContentTypeRegistry()
        site._setObject( ctr.getId(), ctr )

        if mit_predikat:
            for (predicate_id, predicate_type, edit_args, content_type_name
                ) in _TEST_PREDICATES:
                ctr.addPredicate(predicate_id, predicate_type) 
                predicate = ctr.getPredicate(predicate_id)
                predicate.edit(*edit_args)
                ctr.assignTypeName(predicate_id, content_type_name)

        return site

    def setUp(self):
        PlacelessSetup.setUp(self)
        BaseRegistryTests.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore.exportimport)

    def tearDown(self):
        BaseRegistryTests.tearDown(self)
        PlacelessSetup.tearDown(self)


class Test_exportContentTypeRegistry(_ContentTypeRegistrySetup):

    def test_empty(self):
        from Products.CMFSetup.contenttyperegistry \
            import exportContentTypeRegistry

        site = self._initSite(mit_predikat=False)
        context = DummyExportContext(site)
        exportContentTypeRegistry(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'contenttyperegistry.xml')
        self._compareDOM(text, self._EMPTY_EXPORT)
        self.assertEqual(content_type, 'text/xml')

    def test_with_policy(self):
        from Products.CMFSetup.contenttyperegistry \
            import exportContentTypeRegistry

        site = self._initSite(mit_predikat=True)
        context = DummyExportContext(site)
        exportContentTypeRegistry(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'contenttyperegistry.xml')
        self._compareDOM(text, self._WITH_POLICY_EXPORT)
        self.assertEqual(content_type, 'text/xml')


class Test_importContentTypeRegistry(_ContentTypeRegistrySetup):

    def test_normal(self):
        from Products.CMFSetup.contenttyperegistry \
            import importContentTypeRegistry

        site = self._initSite(mit_predikat=False)
        ctr = site.content_type_registry
        self.assertEqual(len(ctr.listPredicates()), 0)

        context = DummyImportContext(site)
        context._files['contenttyperegistry.xml'] = self._WITH_POLICY_EXPORT
        importContentTypeRegistry(context)

        self.assertEqual(len(ctr.listPredicates()), len(_TEST_PREDICATES))

        predicate_id, (predicate, content_type_name) = ctr.listPredicates()[0]
        self.assertEqual(predicate_id, self.MAJOR_MINOR_ID)
        self.assertEqual(predicate.PREDICATE_TYPE, 'major_minor')
        self.assertEqual(content_type_name, self.MAJOR_MINOR_TYPENAME)
        self.assertEqual(predicate.major, self.MAJOR.split(','))
        self.assertEqual(predicate.minor, self.MINOR.split(','))

        predicate_id, (predicate, content_type_name) = ctr.listPredicates()[1]
        self.assertEqual(predicate_id, self.EXTENSION_ID)
        self.assertEqual(predicate.PREDICATE_TYPE, 'extension')
        self.assertEqual(content_type_name, self.EXTENSION_TYPENAME)
        self.assertEqual(predicate.extensions, self.EXTENSIONS.split(','))

        predicate_id, (predicate, content_type_name) = ctr.listPredicates()[2]
        self.assertEqual(predicate_id, self.MIMETYPE_REGEX_ID)
        self.assertEqual(predicate.PREDICATE_TYPE, 'mimetype_regex')
        self.assertEqual(content_type_name, self.MIMETYPE_REGEX_TYPENAME)
        self.assertEqual(predicate.pattern.pattern, self.MIMETYPE_REGEX)

        predicate_id, (predicate, content_type_name) = ctr.listPredicates()[3]
        self.assertEqual(predicate_id, self.NAME_REGEX_ID)
        self.assertEqual(predicate.PREDICATE_TYPE, 'name_regex')
        self.assertEqual(content_type_name, self.NAME_REGEX_TYPENAME)
        self.assertEqual(predicate.pattern.pattern, self.NAME_REGEX)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_exportContentTypeRegistry),
        unittest.makeSuite(Test_importContentTypeRegistry),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')