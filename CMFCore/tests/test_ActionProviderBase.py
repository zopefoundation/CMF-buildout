from unittest import TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFCore.tests.base.testcase import SecurityRequestTest

#
#   We have to import these here to make the "ugly sharing" test case go.
#
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.ActionInformation import ActionInformation


class DummyProvider(ActionProviderBase, DummyTool):

    _actions = ( ActionInformation( id='an_id'
                                  , title='A Title'
                                  , action=''
                                  , condition=''
                                  , permissions=''
                                  , category=''
                                  , visible=0
                                  ), )


class DummyAction:

    def __init__( self, value ):
        self.value = value

    def clone( self ):
        return self.__class__( self.value )

    def __cmp__( self, other ):
        return ( cmp( type( self ), type( other ) )
              or cmp( self.__class__, other.__class__ )
              or cmp( self.value, other.value )
              or 0
               )


class ActionProviderBaseTests(SecurityRequestTest):

    def setUp( self ):
        SecurityRequestTest.setUp(self)
        self.site = DummySite('site').__of__(self.root)
        utool = self.site._setObject( 'portal_url', DummyTool() )
        mtool = self.site._setObject( 'portal_membership', DummyTool() )

    def _makeProvider( self, dummy=0 ):

        klass = dummy and DummyProvider or ActionProviderBase
        return klass()

    def test_addAction( self ):

        apb = self._makeProvider()
        self.failIf( apb._actions )
        old_actions = apb._actions
        apb.addAction( id='foo'
                     , name='foo_action'
                     , action=''
                     , condition=''
                     , permission=''
                     , category=''
                     )
        self.failUnless( apb._actions )
        self.failIf( apb._actions is old_actions )
        # make sure a blank permission gets stored as an empty tuple
        self.assertEqual( apb._actions[0].permissions, () )

    def test_changeActions( self ):

        apb = DummyTool()
        old_actions = list( apb._actions )

        keys = [ ( 'id_%d', None )
               , ( 'name_%d', None )
               , ( 'action_%d', '' )
               , ( 'condition_%d', '' )
               , ( 'permission_%d', None )
               , ( 'category_%d', None )
               , ( 'visible_%d', 0 )
               ]

        properties = {}
        for i in range( len( old_actions ) ):
            for key, value in keys:
                token = key % i
                if value is None:
                    value = token
                properties[ token ] = value

        apb.changeActions( properties=properties )

        marker = []
        for i in range( len( apb._actions ) ):

            for key, value in keys:
                attr = key[ : -3 ]

                if value is None:
                    value = key % i

                if attr == 'name':    # WAAAA
                    attr = 'title'

                if attr == 'permission':    # WAAAA
                    attr = 'permissions'
                    value = ( value, )

                attr_value = getattr( apb._actions[i], attr, marker )
                self.assertEqual( attr_value
                                , value
                                , '%s, %s != %s, %s'
                                  % ( attr, attr_value, key, value )  )
        self.failIf( apb._actions is old_actions )

    def test_deleteActions( self ):

        apb = self._makeProvider()
        apb._actions = tuple( map( DummyAction, [ '0', '1', '2' ] ) )
        apb.deleteActions( selections=(0,2) )
        self.assertEqual( len( apb._actions ), 1 )
        self.failUnless( DummyAction('1') in apb._actions )

    def test_DietersNastySharingBug( self ):

        one = self._makeProvider( dummy=1 )
        another = self._makeProvider( dummy=1 )

        def idify( x ):
            return id( x )

        old_ids = one_ids = map( idify, one.listActions() )
        another_ids = map( idify, another.listActions() )

        self.assertEqual( one_ids, another_ids )

        one.changeActions( { 'id_0'            : 'different_id'
                           , 'name_0'          : 'A Different Title'
                           , 'action_0'        : 'arise_shine'
                           , 'condition_0'     : 'always'
                           , 'permissions_0'   : 'granted'
                           , 'category_0'      : 'quality'
                           , 'visible_0'       : 1
                           } )

        one_ids = map( idify, one.listActions() )
        another_ids = map( idify, another.listActions() )
        self.failIf( one_ids == another_ids )
        self.assertEqual( old_ids, another_ids )

    def test_listActionInfos(self):
        wanted = [{'permissions': '', 'id': 'an_id', 'url': '',
                   'name': 'A Title', 'visible': 0, 'category': 'object'}]

        apb = self.site._setObject( 'portal_apb', self._makeProvider(1) )
        rval = apb.listActionInfos()
        self.assertEqual( rval, [] )
        rval = apb.listActionInfos(check_visibility=0)
        self.assertEqual( rval, wanted )
        rval = apb.listActionInfos('foo/another_id', check_visibility=0)
        self.assertEqual( rval, [] )

    def test_getActionObject(self):
        apb = self.site._setObject( 'portal_apb', self._makeProvider(1) )
        rval = apb.getActionObject('object/an_id')
        self.assertEqual(rval, apb._actions[0])
        rval = apb.getActionObject('object/not_existing_id')
        self.assertEqual(rval, None)
        self.assertRaises(ValueError, apb.getActionObject, 'wrong_format')

    def test_getActionInfo(self):
        wanted = {'permissions': '', 'id': 'an_id', 'url': '',
                  'name': 'A Title', 'visible': 0, 'category': 'object'}

        apb = self.site._setObject( 'portal_apb', self._makeProvider(1) )
        rval = apb.getActionInfo( ('object/an_id',) )
        self.assertEqual( rval, wanted )
        rval = apb.getActionInfo('object/an_id')
        self.assertEqual( rval, wanted )
        self.assertRaises( ValueError,
                           apb.getActionInfo,
                           'object/an_id', check_visibility=1 )

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IActionProvider, ActionProviderBase)


def test_suite():
    return TestSuite((
        makeSuite(ActionProviderBaseTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
