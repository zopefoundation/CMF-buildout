from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

from Products.CMFCore.ContentTypeRegistry import ContentTypeRegistry
from Products.CMFCore.ContentTypeRegistry import ExtensionPredicate
from Products.CMFCore.ContentTypeRegistry import MajorMinorPredicate
from Products.CMFCore.ContentTypeRegistry import MimeTypeRegexPredicate
from Products.CMFCore.ContentTypeRegistry import NameRegexPredicate


class MajorMinorPredicateTests( TestCase ):

    def test_empty( self ):
        pred = MajorMinorPredicate( 'empty' )
        assert pred.getMajorType() == 'None'
        assert pred.getMinorType() == 'None'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )

    def test_simple( self ):
        pred = MajorMinorPredicate( 'plaintext' )
        pred.edit( 'text', 'plain' )
        assert pred.getMajorType() == 'text'
        assert pred.getMinorType() == 'plain'
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'foo', 'text/html', 'asdfljksadf' )
        assert not pred( '', '', '' )
        assert not pred( '', 'asdf', '' )

    def test_wildcard( self ):
        pred = MajorMinorPredicate( 'alltext' )
        pred.edit( 'text', '' )
        assert pred.getMajorType() == 'text'
        assert pred.getMinorType() == ''
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo', 'text/html', 'asdfljksadf' )
        assert not pred( 'foo', 'image/png', 'asdfljksadf' )

        pred.edit( '', 'html' )
        assert pred.getMajorType() == ''
        assert pred.getMinorType() == 'html'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo', 'text/html', 'asdfljksadf' )
        assert not pred( 'foo', 'image/png', 'asdfljksadf' )

    def test_interface(self):
        from Products.CMFCore.interfaces.ContentTypeRegistry \
                import ContentTypeRegistryPredicate \
                as IContentTypeRegistryPredicate

        verifyClass(IContentTypeRegistryPredicate, MajorMinorPredicate)


class ExtensionPredicateTests( TestCase ):

    def test_empty( self ):
        pred = ExtensionPredicate( 'empty' )
        assert pred.getExtensions() == 'None'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'foo.txt', 'text/plain', 'asdfljksadf' )
        assert not pred( 'foo.bar', 'text/html', 'asdfljksadf' )

    def test_simple( self ):
        pred = ExtensionPredicate( 'stardottext' )
        pred.edit( 'txt' )
        assert pred.getExtensions() == 'txt'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo.txt', 'text/plain', 'asdfljksadf' )
        assert not pred( 'foo.bar', 'text/html', 'asdfljksadf' )

    def test_multi( self ):
        pred = ExtensionPredicate( 'stardottext' )
        pred.edit( 'txt text html htm' )
        assert pred.getExtensions() == 'txt text html htm'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo.txt', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo.text', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo.html', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo.htm', 'text/plain', 'asdfljksadf' )
        assert not pred( 'foo.bar', 'text/html', 'asdfljksadf' )

    def test_interface(self):
        from Products.CMFCore.interfaces.ContentTypeRegistry \
                import ContentTypeRegistryPredicate \
                as IContentTypeRegistryPredicate

        verifyClass(IContentTypeRegistryPredicate, ExtensionPredicate)


class MimeTypeRegexPredicateTests( TestCase ):

    def test_empty( self ):
        pred = MimeTypeRegexPredicate( 'empty' )
        assert pred.getPatternStr() == 'None'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )

    def test_simple( self ):
        pred = MimeTypeRegexPredicate( 'plaintext' )
        pred.edit( 'text/plain' )
        assert pred.getPatternStr() == 'text/plain'
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'foo', 'text/html', 'asdfljksadf' )

    def test_pattern( self ):
        pred = MimeTypeRegexPredicate( 'alltext' )
        pred.edit( 'text/*' )
        assert pred.getPatternStr() == 'text/*'
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo', 'text/html', 'asdfljksadf' )
        assert not pred( 'foo', 'image/png', 'asdfljksadf' )

    def test_interface(self):
        from Products.CMFCore.interfaces.ContentTypeRegistry \
                import ContentTypeRegistryPredicate \
                as IContentTypeRegistryPredicate

        verifyClass(IContentTypeRegistryPredicate, MimeTypeRegexPredicate)


class NameRegexPredicateTests( TestCase ):

    def test_empty( self ):
        pred = NameRegexPredicate( 'empty' )
        assert pred.getPatternStr() == 'None'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )

    def test_simple( self ):
        pred = NameRegexPredicate( 'onlyfoo' )
        pred.edit( 'foo' )
        assert pred.getPatternStr() == 'foo'
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'fargo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'bar', 'text/plain', 'asdfljksadf' )

    def test_pattern( self ):
        pred = NameRegexPredicate( 'allfwords' )
        pred.edit( 'f.*' )
        assert pred.getPatternStr() == 'f.*'
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert pred( 'fargo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'bar', 'text/plain', 'asdfljksadf' )

    def test_interface(self):
        from Products.CMFCore.interfaces.ContentTypeRegistry \
                import ContentTypeRegistryPredicate \
                as IContentTypeRegistryPredicate

        verifyClass(IContentTypeRegistryPredicate, NameRegexPredicate)


class ContentTypeRegistryTests( TestCase ):

    def setUp( self ):
        self.reg = ContentTypeRegistry()

    def test_empty( self ):
        reg=self.reg
        assert reg.findTypeName( 'foo', 'text/plain', 'asdfljksadf' ) is None
        assert reg.findTypeName( 'fargo', 'text/plain', 'asdfljksadf' ) is None
        assert reg.findTypeName( 'bar', 'text/plain', 'asdfljksadf' ) is None
        assert not reg.listPredicates()
        self.assertRaises( KeyError, reg.removePredicate, 'xyzzy' )

    def test_reorder( self ):
        reg=self.reg
        predIDs = ( 'foo', 'bar', 'baz', 'qux' )
        for predID in predIDs:
            reg.addPredicate( predID, 'name_regex' )
        ids = tuple( map( lambda x: x[0], reg.listPredicates() ) )
        assert ids == predIDs
        reg.reorderPredicate( 'bar', 3 )
        ids = tuple( map( lambda x: x[0], reg.listPredicates() ) )
        assert ids == ( 'foo', 'baz', 'qux', 'bar' )

    def test_lookup( self ):
        reg=self.reg
        reg.addPredicate( 'image', 'major_minor' )
        reg.getPredicate( 'image' ).edit( 'image', '' )
        reg.addPredicate( 'onlyfoo', 'name_regex' )
        reg.getPredicate( 'onlyfoo' ).edit( 'foo' )
        reg.assignTypeName( 'onlyfoo', 'Foo' )
        assert reg.findTypeName( 'foo', 'text/plain', 'asdfljksadf' ) == 'Foo'
        assert not reg.findTypeName( 'fargo', 'text/plain', 'asdfljksadf' )
        assert not reg.findTypeName( 'bar', 'text/plain', 'asdfljksadf' )
        assert reg.findTypeName( 'foo', '', '' ) == 'Foo'
        assert reg.findTypeName( 'foo', None, None ) == 'Foo'

    def test_interface(self):
        from Products.CMFCore.interfaces.ContentTypeRegistry \
                import ContentTypeRegistry as IContentTypeRegistry

        verifyClass(IContentTypeRegistry, ContentTypeRegistry)


def test_suite():
    return TestSuite((
        makeSuite( MajorMinorPredicateTests ),
        makeSuite( ExtensionPredicateTests ),
        makeSuite( MimeTypeRegexPredicateTests ),
        makeSuite( NameRegexPredicateTests ),
        makeSuite( ContentTypeRegistryTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
