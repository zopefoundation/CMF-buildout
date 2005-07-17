import Zope
import unittest
from Products.CMFCore.tests import test_ContentTypeRegistry
from Products.CMFCore.tests import test_PortalFolder
from Products.CMFCore.tests import test_TypesTool
from Products.CMFCore.tests import test_CatalogTool

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( test_ContentTypeRegistry.test_suite() )
    suite.addTest( test_PortalFolder.test_suite() )
    suite.addTest( test_TypesTool.test_suite() )
    suite.addTest( test_CatalogTool.test_suite() )
    return suite

def run():
    if hasattr( unittest, 'JUnitTextTestRunner' ):
        unittest.JUnitTextTestRunner().run( test_suite() )
    else:
        unittest.TextTestRunner( verbosity=1 ).run( test_suite() )

if __name__ == '__main__':
    run()
