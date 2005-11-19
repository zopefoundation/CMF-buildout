from unittest import TestSuite, makeSuite, main
import Testing
try:
    import Zope2
except ImportError: # BBB: for Zope 2.7
    import Zope as Zope2
Zope2.startup()

from Products.CMFCore.tests.base.testcase import TransactionalTest


class MembershipTests( TransactionalTest ):

    def _makePortal(self):
        # Create a portal instance suitable for testing
        factory = self.root.manage_addProduct['CMFDefault'].addConfiguredSite
        factory('site', 'CMFDefault:default', snapshot=False)

        return self.root.site

    def test_join( self ):
        site = self._makePortal()
        member_id = 'test_user'
        site.portal_registration.addMember( member_id
                                          , 'zzyyzz'
                                          , properties={ 'username': member_id
                                                       , 'email' : 'foo@bar.com'
                                                       }
                                          )
        u = site.acl_users.getUser(member_id)
        self.failUnless(u)

    def test_join_without_email( self ):
        site = self._makePortal()
        self.assertRaises(ValueError,
                          site.portal_registration.addMember,
                          'test_user',
                          'zzyyzz',
                          properties={'username':'test_user', 'email': ''}
                          )

    def test_join_with_variable_id_policies( self ):
        site = self._makePortal()
        member_id = 'test.user'

        # Test with the default policy: Names with "." should fail
        self.assertRaises(ValueError,
                          site.portal_registration.addMember,
                          member_id,
                          'zzyyzz',
                          properties={ 'username':'Test User'
                                     , 'email': 'foo@bar.com'
                                     }
                          )

        # Now change the policy to allow "."
        #import pdb; pdb.set_trace()
        new_pattern = "^[A-Za-z][A-Za-z0-9_\.]*$"
        site.portal_registration.manage_editIDPattern(new_pattern)
        site.portal_registration.addMember( member_id
                                          , 'zzyyzz'
                                          , properties={ 'username': 'TestUser2'
                                                       , 'email' : 'foo@bar.com'
                                                       }
                                          )
        u = site.acl_users.getUser(member_id)
        self.failUnless(u)


def test_suite():
    return TestSuite((
        makeSuite(MembershipTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
