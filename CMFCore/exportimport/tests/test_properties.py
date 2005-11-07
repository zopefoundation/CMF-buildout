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
"""Site properties node adapter unit tests.

$Id$
"""

import unittest
import Testing

from Products.CMFCore.tests.base.testcase import PlacelessSetup
from Products.GenericSetup.testing import NodeAdapterTestCase


_PROPERTIES_XML = """\
<site>
 <property name="title">Foo</property>
 <property name="foo_string" type="string">foo</property>
 <property name="foo_boolean" type="boolean">False</property>
</site>
"""


class PropertiesNodeAdapterTests(PlacelessSetup, NodeAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFCore.exportimport.properties \
                import PropertiesNodeAdapter

        return PropertiesNodeAdapter

    def _populate(self, obj):
        obj._setPropValue('title', 'Foo')
        obj._setProperty('foo_string', 'foo', 'string')
        obj._setProperty('foo_boolean', False, 'boolean')

    def setUp(self):
        from Products.CMFCore.PortalObject import PortalObjectBase
        import Products.CMFCore.exportimport
        import Products.Five
        from Products.Five import zcml

        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore.exportimport)

        self._obj = PortalObjectBase('foo_site')
        self._XML = _PROPERTIES_XML


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PropertiesNodeAdapterTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
