##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for PortalContent module.

$Id$
"""

import unittest
import Testing

from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_base
from zope.testing.cleanup import cleanUp

from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyUserFolder
from Products.CMFCore.tests.base.testcase import SecurityRequestTest
from Products.CMFCore.tests.base.testcase import setUpEvents


class PortalContentTests(unittest.TestCase):

    def test_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFCore.interfaces.Contentish \
                import Contentish as IContentish
        from Products.CMFCore.interfaces.Dynamic \
                import DynamicType as IDynamicType
        from Products.CMFCore.PortalContent import PortalContent

        verifyClass(IContentish, PortalContent)
        verifyClass(IDynamicType, PortalContent)

    def test_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFCore.interfaces import IContentish
        from Products.CMFCore.interfaces import IDynamicType
        from Products.CMFCore.PortalContent import PortalContent

        verifyClass(IContentish, PortalContent)
        verifyClass(IDynamicType, PortalContent)


class TestContentCopyPaste(SecurityRequestTest):

    # Tests related to http://www.zope.org/Collectors/CMF/205
    # Copy/pasting a content item must set ownership to pasting user

    def setUp(self):
        SecurityRequestTest.setUp(self)
        setUpEvents()

        self.root._setObject('site', DummySite('site'))
        self.site = self.root.site
        self.acl_users = self.site._setObject('acl_users', DummyUserFolder())

    def tearDown(self):
        SecurityRequestTest.tearDown(self)
        cleanUp()

    def _initContent(self, folder, id):
        from Products.CMFCore.PortalContent import PortalContent

        c = PortalContent()
        c._setId(id)
        c.meta_type = 'File'
        folder._setObject(id, c)
        return folder._getOb(id)

    def test_CopyPasteSetsOwnership(self):
        # Copy/pasting a File should set new ownership including local roles
        from OFS.Folder import Folder

        acl_users = self.acl_users
        folder1 = self.site._setObject('folder1', Folder('folder1'))
        folder2 = self.site._setObject('folder2', Folder('folder2'))

        newSecurityManager(None, acl_users.user_foo)
        content = self._initContent(folder1, 'content')
        content.manage_setLocalRoles(acl_users.user_foo.getId(), ['Owner'])

        newSecurityManager(None, acl_users.all_powerful_Oz)
        cb = folder1.manage_copyObjects(['content'])
        folder2.manage_pasteObjects(cb)

        # Now test executable ownership and "owner" local role
        # "member" should have both.
        moved = folder2._getOb('content')
        self.assertEqual(aq_base(moved.getOwner()),
                         aq_base(acl_users.all_powerful_Oz))

        local_roles = moved.get_local_roles()
        self.assertEqual(len(local_roles), 1)
        userid, roles = local_roles[0]
        self.assertEqual(userid, acl_users.all_powerful_Oz.getId())
        self.assertEqual(len(roles), 1)
        self.assertEqual(roles[0], 'Owner')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PortalContentTests),
        unittest.makeSuite(TestContentCopyPaste),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
