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
""" Unit tests for GenericSetup export / import support for topics / criteria.

$Id$
"""
import unittest

from DateTime.DateTime import DateTime

from Products.GenericSetup.tests.conformance \
        import ConformsToIFilesystemExporter
from Products.GenericSetup.tests.conformance \
        import ConformsToIFilesystemImporter
from Products.GenericSetup.tests.common import SecurityRequestTest
from Products.GenericSetup.tests.common import DOMComparator
from Products.GenericSetup.tests.common import DummyExportContext
from Products.GenericSetup.tests.common import DummyImportContext

_DATE_STR = '2005-11-20T12:00:00Z'
_CRITERIA_DATA = (
    ('a', 'String Criterion', {'value': 'A'}),
    ('b', 'List Criterion', {'value': ('B', 'b'), 'operator': 'or'}),
    ('c', 'Integer Criterion', {'value': 3, 'direction': 'min'}),
    ('d', 'Friendly Date Criterion', {'value': DateTime(_DATE_STR),
                                      'operation': 'min', 'daterange': 'old'}),
    ('e', 'Sort Criterion', {'reversed': 0}),
)

class TopicExportImportTests(SecurityRequestTest,
                             DOMComparator,
                             ConformsToIFilesystemExporter,
                             ConformsToIFilesystemImporter,
                            ):

    def _getTargetClass(self):
        from Products.CMFTopic.exportimport import TopicExportImport
        return TopicExportImport

    def _makeOne(self, context, *args, **kw):
        return self._getTargetClass()(context, *args, **kw)

    def _makeTopic(self, id, with_criteria=False):
        from Products.CMFTopic.Topic import Topic
        topic = Topic(id)

        if with_criteria:
            for field, c_type, attrs in _CRITERIA_DATA:
                topic.addCriterion(field, c_type)
                criterion = topic.getCriterion(field)
                criterion.edit(**attrs)

        return topic

    def test_listExportableItems(self):
        topic = self._makeTopic('lEI', False).__of__(self.root)
        adapter = self._makeOne(topic)

        self.assertEqual(len(adapter.listExportableItems()), 0)
        topic.addCriterion('field_a', 'String Criterion')
        self.assertEqual(len(adapter.listExportableItems()), 0)

    def test__getExportInfo_empty(self):
        topic = self._makeTopic('empty', False).__of__(self.root)
        adapter = self._makeOne(topic)

        info = adapter._getExportInfo()
        self.assertEqual(len(info['criteria']), 0)

    def test_export_empty(self):
        topic = self._makeTopic('empty', False).__of__(self.root)
        adapter = self._makeOne(topic)

        context = DummyExportContext(topic)
        adapter.export(context, 'test', False)

        self.assertEqual( len( context._wrote ), 2 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'test/empty/.objects' )
        self.assertEqual( text, '' )
        self.assertEqual( content_type, 'text/comma-separated-values' )

        filename, text, content_type = context._wrote[ 1 ]
        self.assertEqual( filename, 'test/empty/criteria.xml' )
        self._compareDOM( text, _EMPTY_TOPIC_CRITERIA )
        self.assertEqual( content_type, 'text/xml' )

    def test__getExportInfo_with_criteria(self):
        topic = self._makeTopic('with_criteria', True).__of__(self.root)
        adapter = self._makeOne(topic)

        info = adapter._getExportInfo()
        self.assertEqual(len(info['criteria']), len(_CRITERIA_DATA))

        for found, expected in zip(info['criteria'], _CRITERIA_DATA):
            self.assertEqual(found['criterion_id'], 'crit__%s' % expected[0])
            self.assertEqual(found['type'], expected[1])

            if 0 and expected[0] == 'e': # field is None for SortCriterion
                self.assertEqual(found['field'], None)
                expected_attributes = expected[2].copy()
                expected_attributes['index'] = expected[0]
                self.assertEqual(dict(found['attributes']), expected_attributes)
            else:
                self.assertEqual(found['field'], expected[0])
                self.assertEqual(dict(found['attributes']), expected[2])

    def test_export_with_string_criterion(self):
        topic = self._makeTopic('with_string', False).__of__(self.root)
        data = _CRITERIA_DATA[0]
        topic.addCriterion(data[0], data[1])
        topic.getCriterion(data[0]).edit(**data[2])
        adapter = self._makeOne(topic)

        context = DummyExportContext(topic)
        adapter.export(context, 'test', False)

        self.assertEqual( len( context._wrote ), 2 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'test/with_string/.objects' )
        self.assertEqual( text, '' )
        self.assertEqual( content_type, 'text/comma-separated-values' )

        filename, text, content_type = context._wrote[ 1 ]
        self.assertEqual( filename, 'test/with_string/criteria.xml' )
        self._compareDOM( text, _STRING_TOPIC_CRITERIA )
        self.assertEqual( content_type, 'text/xml' )

_EMPTY_TOPIC_CRITERIA = """\
<?xml version="1.0" ?>
<criteria>
</criteria>
"""

_STRING_TOPIC_CRITERIA = """\
<?xml version="1.0" ?>
<criteria>
 <criterion
    criterion_id="crit__a"
    type="String Criterion"
    field="a">
  <attribute name="value" value="A" />
 </criterion>
</criteria>
"""

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TopicExportImportTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

