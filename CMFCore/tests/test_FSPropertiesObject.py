import unittest

from zope.component import getSiteManager

from Products.CMFCore.interfaces import ISkinsTool
from Products.CMFCore.tests.base.testcase import FSDVTest
from Products.CMFCore.tests.base.testcase import SecurityTest

class FSPOTests(SecurityTest, FSDVTest):

    def setUp( self ):
        FSDVTest.setUp(self)
        SecurityTest.setUp( self )

    def tearDown( self ):
        SecurityTest.tearDown( self )
        FSDVTest.tearDown(self)

    def _getTargetClass( self ):
        from Products.CMFCore.FSPropertiesObject import FSPropertiesObject
        return FSPropertiesObject

    def _makeOne( self, id, filename ):
        from os.path import join
        path = join(self.skin_path_name, filename)
        return self._getTargetClass()( id, path ) 

    def _makeContext( self, po_id, po_filename ):
        from OFS.Folder import Folder

        self.root._setObject( 'portal_skins', Folder( 'portal_skins' ) )
        skins = self.root.portal_skins
        sm = getSiteManager()
        sm.registerUtility(skins, ISkinsTool)

        skins._setObject( 'custom', Folder( 'custom' ) )
        custom = skins.custom

        skins._setObject( 'fsdir', Folder( 'fsdir' ) )
        fsdir = skins.fsdir

        fsdir._setObject( 'test_props', self._makeOne( po_id, po_filename ) )
        fspo = fsdir.test_props

        return custom, fsdir, fspo

    def test__readFile( self ):
        from DateTime.DateTime import DateTime

        custom, fsdir, fspo = self._makeContext( 'test_props'
                                               , 'test_props.props')

        self.assertEqual( fspo.getProperty( 'title' ), 'Test properties' )
        self.assertEqual( fspo.getProperty( 'value1' ), 'one' )
        self.assertEqual( fspo.getProperty( 'value2' ), 'two' )
        self.assertEqual( fspo.getProperty( 'an_int' ), 42 )
        self.assertEqual( fspo.getProperty( 'a_float' ), 3.1415926 )
        self.assertEqual( fspo.getProperty( 'a_boolean' ), False )
        self.assertEqual( fspo.getProperty( 'a_long' ), 40000000000 )
        self.assertEqual( fspo.getProperty( 'a_date' )
                        , DateTime( '01/01/2001' ) )
        self.assertEqual( fspo.getProperty( 'a_tokens' )
                        , [ 'peter', 'paul', 'mary' ] )

    def test__createZODBClone( self ):

        from OFS.Folder import Folder

        custom, fsdir, fspo = self._makeContext( 'test_props'
                                               , 'test_props.props')

        target = fspo._createZODBClone()
        self.failUnless( isinstance( target, Folder ) )
        for prop_id in fspo.propertyIds():
            self.assertEqual( target.getProperty( prop_id )
                            , fspo.getProperty( prop_id ) )

    def test_manage_doCustomize( self ):
        custom, fsdir, fspo = self._makeContext( 'test_props'
                                               , 'test_props.props')

        fspo.manage_doCustomize( folder_path='custom' )

        self.assertEqual( len( custom.objectIds() ), 1 )
        self.failUnless( 'test_props' in custom.objectIds() )  


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( FSPOTests ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
