import Zope
from unittest import main
from Products.CMFCore.tests.base.utils import build_test_suite

def suite():

    return build_test_suite('Products.CMFDefault.tests',[
        'test_Discussions',
        'test_DublinCore',
        'test_Document',
        'test_NewsItem',
        'test_Link',
        'test_Favorite',
        'test_Image',
        'test_MetadataTool',
        'test_utils',
        'test_join',
        'test_Portal',
        'test_DiscussionTool',
        'test_MembershipTool',
        'test_PropertiesTool',
        'test_RegistrationTool',
        'test_DefaultWorkflow',
        ])

def test_suite():
    # Just toilence the top-level test.py
    return None

if __name__ == '__main__':
    main(defaultTest='suite')
