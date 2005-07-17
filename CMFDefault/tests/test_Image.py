import Zope
from unittest import TestCase, TestSuite, makeSuite, main

import os, cStringIO

from Products.CMFDefault.File import File
from Products.CMFDefault.Image import Image
from Products.CMFDefault import tests

TESTS_HOME = tests.__path__[0]
TEST_JPG = os.path.join(TESTS_HOME, 'TestImage.jpg')

class TestImageElement(TestCase):

    def test_EditWithEmptyFile(self):
        """ Test handling of empty file uploads """
        image = Image('testimage')

        testfile = open(TEST_JPG, 'rb')
        image.edit(file=testfile)
        testfile.seek(0,2)
        testfilesize = testfile.tell()
        testfile.close()

        assert image.get_size() == testfilesize

        emptyfile = cStringIO.StringIO()
        image.edit(file=emptyfile)

        assert image.get_size() > 0
        assert image.get_size() == testfilesize

    def test_File_setFormat(self):
        """ Setting the format must also set the content_type property """
        file = File('testfile', format='image/jpeg')
        self.assertEqual(file.Format(), 'image/jpeg')
        self.assertEqual(file.content_type, 'image/jpeg')
        file.setFormat('image/gif')
        self.assertEqual(file.Format(), 'image/gif')
        self.assertEqual(file.content_type, 'image/gif')
 
    def test_Image_setFormat(self):
        """ Setting the format must also set the content_type property """
        image = Image('testimage', format='image/jpeg')
        self.assertEqual(image.Format(), 'image/jpeg')
        self.assertEqual(image.content_type, 'image/jpeg')
        image.setFormat('image/gif')
        self.assertEqual(image.Format(), 'image/gif')
        self.assertEqual(image.content_type, 'image/gif')
 

def test_suite():
    return TestSuite((
        makeSuite(TestImageElement),
        ))
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
