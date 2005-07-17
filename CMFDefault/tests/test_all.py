##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFDefault tests.

$Id$
"""

from unittest import main
import Testing
import Zope
Zope.startup()

from Products.CMFCore.tests.base.utils import build_test_suite


def suite():
    return build_test_suite('Products.CMFDefault.tests',[
        'test_DefaultWorkflow',
        'test_Discussions',
        'test_DiscussionTool',
        'test_Document',
        'test_DublinCore',
        'test_Favorite',
        'test_Image',
        'test_join',
        'test_Link',
        'test_MembershipTool',
        'test_MetadataTool',
        'test_NewsItem',
        'test_Portal',
        'test_PropertiesTool',
        'test_RegistrationTool',
        'test_utils',
        ])

def test_suite():
    # Just to silence the top-level test.py
    return None

if __name__ == '__main__':
    main(defaultTest='suite')
