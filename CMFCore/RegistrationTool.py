##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################

""" Basic user registration tool.

$Id$
"""

from Globals import InitializeClass
from Globals import DTMLFile
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo

from ActionProviderBase import ActionProviderBase

from CMFCorePermissions import AddPortalMember
from CMFCorePermissions import MailForgottenPassword
from CMFCorePermissions import SetOwnPassword
from CMFCorePermissions import SetOwnProperties
from CMFCorePermissions import ManagePortal

from utils import UniqueObject
from utils import _checkPermission
from utils import _getAuthenticatedUser
from utils import _limitGrantedRoles
from utils import getToolByName
from utils import _dtmldir


class RegistrationTool(UniqueObject, SimpleItem, ActionProviderBase):

    """ Create and modify users by making calls to portal_membership.
    """
    id = 'portal_registration'
    meta_type = 'CMF Registration Tool'

    security = ClassSecurityInfo()

    manage_options = (ActionProviderBase.manage_options +
                     ({ 'label' : 'Overview', 'action' : 'manage_overview' }
                     , 
                     ) + SimpleItem.manage_options)

    #
    #   ZMI methods
    #
    security.declareProtected( ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainRegistrationTool', _dtmldir )

    #
    #   'portal_registration' interface methods
    #
    security.declarePrivate('listActions')
    def listActions(self, info):
        return None 

    security.declarePublic('isRegistrationAllowed')
    def isRegistrationAllowed(self, REQUEST):
        '''Returns a boolean value indicating whether the user
        is allowed to add a member to the portal.
        '''
        return _checkPermission('Add Portal Member', self.aq_inner.aq_parent)

    security.declarePublic('testPasswordValidity')
    def testPasswordValidity(self, password, confirm=None):
        '''If the password is valid, returns None.  If not, returns
        a string explaining why.
        '''
        return None

    security.declarePublic('testPropertiesValidity')
    def testPropertiesValidity(self, new_properties, member=None):
        '''If the properties are valid, returns None.  If not, returns
        a string explaining why.
        '''
        return None

    security.declarePublic('generatePassword')
    def generatePassword(self):
        '''Generates a password which is guaranteed to comply
        with the password policy.
        '''
        import string, random
        chars = string.lowercase[:26] + string.uppercase[:26] + string.digits
        result = []
        for n in range(6):
            result.append(random.choice(chars))
        return string.join(result, '')

    security.declareProtected(AddPortalMember, 'addMember')
    def addMember(self, id, password, roles=('Member',), domains='',
                  properties=None):
        '''Creates a PortalMember and returns it. The properties argument
        can be a mapping with additional member properties. Raises an
        exception if the given id already exists, the password does not
        comply with the policy in effect, or the authenticated user is not
        allowed to grant one of the roles listed (where Member is a special
        role that can always be granted); these conditions should be
        detected before the fact so that a cleaner message can be printed.
        '''
        if not self.isMemberIdAllowed(id):
            raise ValueError('The login name you selected is already '
                             'in use or is not valid. Please choose another.')

        failMessage = self.testPasswordValidity(password)
        if failMessage is not None:
            raise ValueError(failMessage)

        if properties is not None:
            failMessage = self.testPropertiesValidity(properties)
            if failMessage is not None:
                raise ValueError(failMessage)

        # Limit the granted roles.
        # Anyone is always allowed to grant the 'Member' role.
        _limitGrantedRoles(roles, self, ('Member',))

        membership = getToolByName(self, 'portal_membership')
        membership.addMember(id, password, roles, domains, properties)

        member = membership.getMemberById(id)
        self.afterAdd(member, id, password, properties)
        return member

    import re
    __ALLOWED_MEMBER_ID_PATTERN = re.compile( "^[A-Za-z][A-Za-z0-9_]*$" )
    security.declareProtected(AddPortalMember, 'isMemberIdAllowed')
    def isMemberIdAllowed(self, id):
        '''Returns 1 if the ID is not in use and is not reserved.
        '''
        if len(id) < 1 or id == 'Anonymous User':
            return 0
        if not self.__ALLOWED_MEMBER_ID_PATTERN.match( id ):
            return 0
        membership = getToolByName(self, 'portal_membership')
        if membership.getMemberById(id) is not None:
            return 0
        return 1

    security.declarePublic('afterAdd')
    def afterAdd(self, member, id, password, properties):
        '''Called by portal_registration.addMember()
        after a member has been added successfully.'''
        pass

    security.declareProtected(MailForgottenPassword, 'mailPassword')
    def mailPassword(self, forgotten_userid, REQUEST):
        '''Email a forgotten password to a member.  Raises an exception
        if user ID is not found.
        '''
        raise 'NotImplemented'

InitializeClass(RegistrationTool)
