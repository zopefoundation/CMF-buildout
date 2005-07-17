import unittest
import Zope
from Products.CMFCore.tests.base.utils import build_test_suite

def suite():
    return build_test_suite('Products.CMFCalendar.tests',
                            ['test_Event',
                             'test_Calendar'])

def test_suite():
    # Just toilence the top-level test.py
    return None

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
