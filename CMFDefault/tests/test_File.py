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
""" Unit tests for File module.

$Id$
"""

import unittest
import Testing

from os.path import join as path_join

from Products.CMFDefault import tests

from common import ConformsToContent

TESTS_HOME = tests.__path__[0]
TEST_JPG = path_join(TESTS_HOME, 'TestImage.jpg')


class FileTests(ConformsToContent, unittest.TestCase):

    def _getTargetClass(self):
        from Products.CMFDefault.File import File

        return File

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_File_setFormat(self):
        # Setting the DC.format must also set the content_type property
        file = self._makeOne('testfile', format='image/jpeg')
        self.assertEqual(file.Format(), 'image/jpeg')
        self.assertEqual(file.content_type, 'image/jpeg')
        file.setFormat('image/gif')
        self.assertEqual(file.Format(), 'image/gif')
        self.assertEqual(file.content_type, 'image/gif')

    def test_FileContentTypeUponConstruction(self):
        # Test the content type after calling the constructor with the
        # file object being passed in (http://www.zope.org/Collectors/CMF/370)
        testfile = open(TEST_JPG, 'rb')
        # Notice the cheat? File objects lack the extra intelligence that
        # picks content types from the actual file data, so it needs to be
        # helped along with a file extension...
        file = self._makeOne('testfile.jpg', file=testfile)
        testfile.close()
        self.assertEqual(file.Format(), 'image/jpeg')
        self.assertEqual(file.content_type, 'image/jpeg')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FileTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
