from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()

from os.path import join as path_join
from cStringIO import StringIO

from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFDefault import tests
from Products.CMFDefault.Image import Image

TESTS_HOME = tests.__path__[0]
TEST_JPG = path_join(TESTS_HOME, 'TestImage.jpg')


class TestImageElement(TestCase):

    def setUp(self):
        self.site = DummySite('site')
        self.site._setObject( 'portal_membership', DummyTool() )

    def test_EditWithEmptyFile(self):
        # Test handling of empty file uploads
        image = self.site._setObject( 'testimage', Image('testimage') )

        testfile = open(TEST_JPG, 'rb')
        image.edit(file=testfile)
        testfile.seek(0,2)
        testfilesize = testfile.tell()
        testfile.close()

        assert image.get_size() == testfilesize

        emptyfile = StringIO()
        image.edit(file=emptyfile)

        assert image.get_size() > 0
        assert image.get_size() == testfilesize


def test_suite():
    return TestSuite((
        makeSuite(TestImageElement),
        ))
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
