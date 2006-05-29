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
""" Unit tests for CMFBTreeFolder module.

$Id$
"""

import unittest
import Testing
import Zope2
Zope2.startup()

from Products.CMFCore.testing import ConformsToFolder


class CMFBTreeFolderTests(ConformsToFolder, unittest.TestCase):

    def _getTargetClass(self):
        from Products.CMFCore.CMFBTreeFolder import CMFBTreeFolder

        return CMFBTreeFolder

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_empty( self ):
        empty = self._makeOne('test')
        self.assertEqual( len( empty.objectIds() ), 0 )

    def test___module_aliases__( self ):
        from Products.BTreeFolder2.CMFBTreeFolder \
            import CMFBTreeFolder as BBB

        self.failUnless( BBB is self._getTargetClass() )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CMFBTreeFolderTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
