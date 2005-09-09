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

from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope2
Zope2.startup()

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.User import UnrestrictedUser
from Acquisition import aq_base
import transaction

from Products.CMFCore.tests.base.testcase import SecurityRequestTest


class PortalContentTests(TestCase):

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

    def _initFolders(self):
        from OFS.Folder import Folder

        FOLDER_IDS = ( 'acl_users', 'folder1', 'folder2' )

        for folder_id in FOLDER_IDS:
            if folder_id not in self.root.objectIds():
                self.root._setObject( folder_id, Folder( folder_id ) )

        # Hack, we need a _p_mtime for the file, so we make sure that it
        # has one. We use a subtransaction, which means we can rollback
        # later and pretend we didn't touch the ZODB.
        #transaction.commit(1)

        return [ self.root._getOb( folder_id ) for folder_id in FOLDER_IDS ]

    def _initContent(self, folder, id):
        from Products.CMFCore.PortalContent import PortalContent

        c = PortalContent()
        c._setId(id)
        c.meta_type = 'File'
        folder._setObject(id, c)
        return folder._getOb(id)

    def test_CopyPasteSetsOwnership(self):
        # Copy/pasting a File should set new ownership including local roles

        acl_users, folder1, folder2 = self._initFolders()
        acl_users._doAddUser('user1', '', ('Member',), ())
        user1 = acl_users.getUserById('user1').__of__(acl_users)
        acl_users._doAddUser('user2', '', ('Member',), ())
        user2 = acl_users.getUserById('user2').__of__(acl_users)

        newSecurityManager(None, user1)
        content = self._initContent(folder1, 'content')
        content.manage_setLocalRoles(user1.getId(), ['Owner'])

        newSecurityManager(None, user2)
        cb = folder1.manage_copyObjects(['content'])
        folder2.manage_pasteObjects(cb)

        # Now test executable ownership and "owner" local role
        # "member" should have both.
        moved = folder2._getOb('content')
        self.assertEqual(aq_base(moved.getOwner()), aq_base(user2))

        local_roles = moved.get_local_roles()
        self.assertEqual(len(local_roles), 1)
        userid, roles = local_roles[0]
        self.assertEqual(userid, user2.getId())
        self.assertEqual(len(roles), 1)
        self.assertEqual(roles[0], 'Owner')


def test_suite():
    return TestSuite((
        makeSuite(PortalContentTests),
        makeSuite(TestContentCopyPaste),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
