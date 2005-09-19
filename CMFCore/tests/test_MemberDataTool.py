from unittest import TestCase, TestSuite, makeSuite, main

import Zope
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

import Acquisition
from Products.CMFCore.MemberDataTool import MemberDataTool
from Products.CMFCore.MemberDataTool import MemberData

class DummyUserFolder(Acquisition.Implicit):

    def __init__(self):
        self._users = {}

    def _addUser(self, user):
        self._users[user.getUserName()] = user

    def userFolderEditUser(self, name, password, roles, domains):
        user = self._users[name]
        if password is not None:
            user.__ = password
        # Emulate AccessControl.User's stupid behavior (should test None)
        user.roles = tuple(roles)
        user.domains = tuple(domains)

    def getUsers(self):
        return self._users.values()


class DummyUser(Acquisition.Implicit):

    def __init__(self, name, password, roles, domains):
        self.name = name
        self.__ = password
        self.roles = tuple(roles)
        self.domains = tuple(domains)

    def getUserName(self):
        return self.name

    def getRoles(self):
        return self.roles + ('Authenticated',)

    def getDomains(self):
        return self.domains


class MemberDataToolTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_memberdata \
                import portal_memberdata as IMemberDataTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IMemberDataTool, MemberDataTool)
        verifyClass(IActionProvider, MemberDataTool)

    def test_deleteMemberData(self):
        tool = MemberDataTool()
        tool.registerMemberData('Dummy', 'user_foo')
        self.failUnless( tool._members.has_key('user_foo') )
        self.failUnless( tool.deleteMemberData('user_foo') )
        self.failIf( tool._members.has_key('user_foo') )
        self.failIf( tool.deleteMemberData('user_foo') )

    def test_pruneMemberData(self):
        # This needs a tad more setup
        from OFS.Folder import Folder
        from Products.CMFCore.MembershipTool import MembershipTool
        folder = Folder('test')
        folder._setObject('portal_memberdata', MemberDataTool())
        folder._setObject('portal_membership', MembershipTool())
        folder._setObject('acl_users', DummyUserFolder())
        tool = folder.portal_memberdata

        # Create some members
        for i in range(20):
            tool.registerMemberData( 'Dummy_%i' % i
                                   , 'user_foo_%i' % i
                                   )

        # None of these fake members are in the user folder, which means
        # there are 20 members and 20 "orphans"
        contents = tool.getMemberDataContents()
        info_dict = contents[0]
        self.assertEqual(info_dict['member_count'], 20)
        self.assertEqual(info_dict['orphan_count'], 20)

        # Calling the prune method should delete all orphans, so we end
        # up with no members in the tool.
        tool.pruneMemberDataContents()
        contents = tool.getMemberDataContents()
        info_dict = contents[0]
        self.assertEqual(info_dict['member_count'], 0)
        self.assertEqual(info_dict['orphan_count'], 0)


class MemberDataTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_memberdata \
                import MemberData as IMemberData

        verifyClass(IMemberData, MemberData)


def test_suite():
    return TestSuite((
        makeSuite( MemberDataToolTests ),
        makeSuite( MemberDataTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
