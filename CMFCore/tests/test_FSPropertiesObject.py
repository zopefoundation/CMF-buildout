import unittest

from os.path import join

from OFS.Folder import Folder

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
        path = join(self.skin_path_name, filename)
        return self._getTargetClass()( id, path ) 

    def _makeContext( self, po_id, po_filename ):
        self.root._setObject( 'portal_skins', Folder( 'portal_skins' ) )
        skins = self.root.portal_skins

        skins._setObject( 'custom', Folder( 'custom' ) )
        custom = skins.custom

        skins._setObject( 'fsdir', Folder( 'fsdir' ) )
        fsdir = skins.fsdir

        fsdir._setObject( 'test_props', self._makeOne( po_id, po_filename ) )
        fspo = fsdir.test_props

        return custom, fsdir, fspo

    def test_customize( self ):

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
