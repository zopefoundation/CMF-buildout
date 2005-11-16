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
"""Content type registry node adapter unit tests.

$Id: test_contenttyperegistry.py 40087 2005-11-13 19:55:09Z yuppie $
"""

import unittest
import Testing

from Products.CMFCore.tests.base.testcase import PlacelessSetup
from Products.GenericSetup.testing import NodeAdapterTestCase


_CTR_XML = """\
<object name="content_type_registry" meta_type="Content Type Registry">
 <predicate name="foo_predicate" content_type_name="Foo Type"
    predicate_type="major_minor">
  <argument value="foo_major"/>
  <argument value="foo_minor"/>
 </predicate>
 <predicate name="bar_predicate" content_type_name="Bar Type"
    predicate_type="extension">
  <argument value="bar"/>
 </predicate>
 <predicate name="baz_predicate" content_type_name="Baz Type"
    predicate_type="mimetype_regex">
  <argument value="baz/.*"/>
 </predicate>
 <predicate name="foobar_predicate" content_type_name="Foobar Type"
    predicate_type="name_regex">
  <argument value="foobar-.*"/>
 </predicate>
</object>
"""


class ContentTypeRegistryNodeAdapterTests(PlacelessSetup,
                                          NodeAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFCore.exportimport.contenttyperegistry \
                import ContentTypeRegistryNodeAdapter

        return ContentTypeRegistryNodeAdapter

    def _populate(self, obj):
        obj.addPredicate('foo_predicate', 'major_minor')
        obj.getPredicate('foo_predicate').edit('foo_major', 'foo_minor')
        obj.assignTypeName('foo_predicate', 'Foo Type')
        obj.addPredicate('bar_predicate', 'extension')
        obj.getPredicate('bar_predicate').edit('bar')
        obj.assignTypeName('bar_predicate', 'Bar Type')
        obj.addPredicate('baz_predicate', 'mimetype_regex')
        obj.getPredicate('baz_predicate').edit('baz/.*')
        obj.assignTypeName('baz_predicate', 'Baz Type')
        obj.addPredicate('foobar_predicate', 'name_regex')
        obj.getPredicate('foobar_predicate').edit('foobar-.*')
        obj.assignTypeName('foobar_predicate', 'Foobar Type')

    def setUp(self):
        from Products.CMFCore.ContentTypeRegistry import ContentTypeRegistry
        import Products.CMFCore.exportimport
        import Products.Five
        from Products.Five import zcml

        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore.exportimport)

        self._obj = ContentTypeRegistry()
        self._XML = _CTR_XML


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ContentTypeRegistryNodeAdapterTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
