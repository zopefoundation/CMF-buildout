import Zope
from unittest import main
from Products.CMFCore.tests.base.utils import build_test_suite

def suite():

    return build_test_suite('Products.CMFTopic.tests',[
        'test_Topic',
        'test_DateC',
        'test_ListC',
        'test_SIC',
        'test_SSC',
        ])

def test_suite():
    # Just toilence the top-level test.py
    return None

if __name__ == '__main__':
    main(defaultTest='suite')
