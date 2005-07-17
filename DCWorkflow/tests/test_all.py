"""Currently all stub, no substance."""
import unittest
from Products.CMFCore.tests.base.utils import build_test_suite

def suite():
    return unittest.TestSuite()

def test_suite():
    # Just toilence the top-level test.py
    return None

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
