from unittest import TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()

from AccessControl import getSecurityManager
from AccessControl.Owned import Owned
from AccessControl.Permission import Permission

from Products.CMFCore.tests.base.dummy import DummyObject
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyUserFolder
from Products.CMFCore.tests.base.testcase import SecurityTest
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import normalize
from Products.CMFCore.utils import keywordsplitter
from Products.CMFCore.utils import contributorsplitter


class DummyObject(Owned, DummyObject):
    pass


class CoreUtilsTests(SecurityTest):

    def setUp(self):
        SecurityTest.setUp(self)
        self.site = DummySite('site').__of__(self.root)
        self.site._setObject( 'acl_users', DummyUserFolder() )
        self.site._setObject('content_dummy', DummyObject(id='content_dummy'))
        self.site._setObject('actions_dummy', DummyObject(id='actions_dummy'))

    def test__checkPermission(self):
        o = self.site.actions_dummy
        Permission('View',(),o).setRoles(('Anonymous',))
        Permission('WebDAV access',(),o).setRoles(('Authenticated',))
        Permission('Manage users',(),o).setRoles(('Manager',))
        eo = self.site.content_dummy
        eo._owner = (['acl_users'], 'user_foo')
        getSecurityManager().addContext(eo)
        self.failUnless( _checkPermission('View', o) )
        self.failIf( _checkPermission('WebDAV access', o) )
        self.failIf( _checkPermission('Manage users', o) )

        eo._proxy_roles = ('Authenticated',)
        self.failIf( _checkPermission('View', o) )
        self.failUnless( _checkPermission('WebDAV access', o) )
        self.failIf( _checkPermission('Manage users', o) )

    def test_normalize(self):
        self.assertEqual( normalize('foo/bar'), 'foo/bar' )
        self.assertEqual( normalize('foo\\bar'), 'foo/bar' )

    def test_keywordsplitter_empty(self):
        for x in [ '', ' ', ',', ',,', ';', ';;' ]:
            self.assertEqual( keywordsplitter({'Keywords': x}), 
                              [] )

    def test_keywordsplitter_single(self):
        for x in [ 'foo', ' foo ', 'foo,', 'foo ,,', 'foo;', 'foo ;;' ]:
            self.assertEqual( keywordsplitter({'Keywords': x}), 
                              ['foo'] )

    def test_keywordsplitter_multi(self):
        for x in [ 'foo, bar, baz'
                 , 'foo, bar , baz'
                 , 'foo, bar,, baz'
                 , 'foo; bar; baz'
                 ]:
            self.assertEqual( keywordsplitter({'Keywords': x}), 
                              ['foo', 'bar', 'baz'] )

    def test_contributorsplitter_emtpy(self):
        for x in [ '', ' ', ';', ';;' ]:
            self.assertEqual( contributorsplitter({'Contributors': x}), 
                              [] )

    def test_contributorsplitter_single(self):
        for x in [ 'foo', ' foo ', 'foo;', 'foo ;;' ]:
            self.assertEqual( contributorsplitter({'Contributors': x}), 
                              ['foo'] )

    def test_contributorsplitter_multi(self):
        for x in [ 'foo; bar; baz'
                 , 'foo; bar ; baz'
                 , 'foo; bar;; baz'
                 ]:
            self.assertEqual( contributorsplitter({'Contributors': x}), 
                              ['foo', 'bar', 'baz'] )


def test_suite():
    return TestSuite((
        makeSuite(CoreUtilsTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
