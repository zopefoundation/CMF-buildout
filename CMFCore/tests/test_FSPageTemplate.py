import unittest
import Zope

class DummyCachingManager:
    def getHTTPCachingHeaders( self, content, view_name, keywords, time=None ):
        return ( ( 'foo', 'Foo' ), ( 'bar', 'Bar' ) )

from Products.CMFCore.tests.base.testcase import RequestTest, SecurityTest

class FSPTMaker:

    def _makeOne( self, id, filename ):

        from Products.CMFCore.FSPageTemplate import FSPageTemplate
        from Products.CMFCore.tests.test_DirectoryView import skin_path_name
        from os.path import join

        return FSPageTemplate( id, join( skin_path_name, filename ) )

class FSPageTemplateTests( RequestTest, FSPTMaker ):

    def test_Call( self ):

        script = self._makeOne( 'testPT', 'testPT.pt' )
        script = script.__of__(self.root)
        self.assertEqual(script(),'foo\n')
        
    def test_ContentType(self):
        script = self._makeOne( 'testXMLPT', 'testXMLPT.pt' )
        script = script.__of__(self.root)
        script()
        self.assertEqual(script.content_type, 'text/xml')
        self.assertEqual(self.RESPONSE.getHeader('content-type'), 'text/xml')
        # purge RESPONSE Content-Type header for new test
        del self.RESPONSE.headers['content-type']
        script = self._makeOne( 'testPT', 'testPT.pt' )
        script = script.__of__(self.root)
        script()
        self.assertEqual(script.content_type, 'text/html')
        self.assertEqual(self.RESPONSE.getHeader('content-type'), 'text/html')

    def test_ContentTypeOverride(self):
        script = self._makeOne( 'testPT_utf8', 'testPT_utf8.pt' )
        script = script.__of__(self.root)
        script()
        self.assertEqual(self.RESPONSE.getHeader('content-type'), 'text/html; charset=utf-8')

    def test_BadCall( self ):

        from Products.PageTemplates.TALES import Undefined
        script = self._makeOne( 'testPTbad', 'testPTbad.pt' )
        script = script.__of__(self.root)

        try: # can't use assertRaises, because different types raised.
            script()
        except (Undefined, KeyError):
            pass
        else:
            self.fail('Calling a bad template did not raise an exception')

    def test_caching( self ):
        """
            Test HTTP caching headers.
        """
        self.root.caching_policy_manager = DummyCachingManager()
        original_len = len( self.RESPONSE.headers )
        script = self._makeOne('testPT', 'testPT.pt')
        script = script.__of__(self.root)
        script()
        self.failUnless( len( self.RESPONSE.headers ) >= original_len + 2 )
        self.failUnless( 'foo' in self.RESPONSE.headers.keys() )
        self.failUnless( 'bar' in self.RESPONSE.headers.keys() )

class FSPageTemplateCustomizationTests( SecurityTest, FSPTMaker ):

    def setUp( self ):

        from OFS.Folder import Folder

        SecurityTest.setUp( self )

        self.root._setObject( 'portal_skins', Folder( 'portal_skins' ) )
        self.skins = self.root.portal_skins

        self.skins._setObject( 'custom', Folder( 'custom' ) )
        self.custom = self.skins.custom

        self.skins._setObject( 'fsdir', Folder( 'fsdir' ) )
        self.fsdir = self.skins.fsdir

        self.fsdir._setObject( 'testPT'
                             , self._makeOne( 'testPT', 'testPT.pt' ) )

        self.fsPT = self.fsdir.testPT

    def test_customize( self ):

        self.fsPT.manage_doCustomize( folder_path='custom' )

        self.assertEqual( len( self.custom.objectIds() ), 1 )
        self.failUnless( 'testPT' in self.custom.objectIds() )

    def test_dontExpandOnCreation( self ):

        self.fsPT.manage_doCustomize( folder_path='custom' )

        customized = self.custom.testPT
        self.failIf( customized.expand )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FSPageTemplateTests),
        unittest.makeSuite(FSPageTemplateCustomizationTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

