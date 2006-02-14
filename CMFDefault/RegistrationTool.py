##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFDefault portal_registration tool.

$Id$
"""

import re

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Globals import InitializeClass

from Products.CMFCore.RegistrationTool import RegistrationTool as BaseTool
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName

from permissions import ManagePortal
from utils import Message as _


class RegistrationTool(BaseTool):

    """ Manage through-the-web signup policies.
    """

    __implements__ = BaseTool.__implements__

    meta_type = 'Default Registration Tool'

    security = ClassSecurityInfo()

    #
    #   'portal_registration' interface
    #
    security.declarePublic( 'testPasswordValidity' )
    def testPasswordValidity(self, password, confirm=None):

        """ Verify that the password satisfies the portal's requirements.

        o If the password is valid, return None.
        o If not, return a string explaining why.
        """
        if not password:
            return _(u'You must enter a password.')

        if len(password) < 5 and not _checkPermission(ManagePortal, self):
            return _(u'Your password must contain at least 5 characters.')

        if confirm is not None and confirm != password:
            return _(u'Your password and confirmation did not match. '
                     u'Please try again.')

        return None

    security.declarePublic( 'testPropertiesValidity' )
    def testPropertiesValidity(self, props, member=None):

        """ Verify that the properties supplied satisfy portal's requirements.

        o If the properties are valid, return None.
        o If not, return a string explaining why.
        """
        if member is None: # New member.

            username = props.get('username', '')
            if not username:
                return _(u'You must enter a valid name.')

            if not self.isMemberIdAllowed(username):
                return _(u'The login name you selected is already in use or '
                         u'is not valid. Please choose another.')

            email = props.get('email')
            if email is None:
                return _(u'You must enter an email address.')

            ok, message =  _checkEmail( email )
            if not ok:
                return _(u'You must enter a valid email address.')

        else: # Existing member.
            email = props.get('email')

            if email is not None:

                ok, message =  _checkEmail( email )
                if not ok:
                    return _(u'You must enter a valid email address.')

            # Not allowed to clear an existing non-empty email.
            existing = member.getProperty('email')

            if existing and email == '':
                return _(u'You must enter a valid email address.')

        return None

    security.declarePublic( 'mailPassword' )
    def mailPassword(self, forgotten_userid, REQUEST):
        """ Email a forgotten password to a member.

        o Raise an exception if user ID is not found.
        """
        membership = getToolByName(self, 'portal_membership')
        member = membership.getMemberById(forgotten_userid)

        if member is None:
            raise ValueError(_(u'The username you entered could not be '
                               u'found.'))

        # assert that we can actually get an email address, otherwise
        # the template will be made with a blank To:, this is bad
        if not member.getProperty('email'):
            raise ValueError(_(u'That user does not have an email address.'))

        check, msg = _checkEmail(member.getProperty('email'))
        if not check:
            raise ValueError, msg

        # Rather than have the template try to use the mailhost, we will
        # render the message ourselves and send it from here (where we
        # don't need to worry about 'UseMailHost' permissions).
        method = getattr(self, 'member_password_mail')
        kw = {'member': member, 'password': member.getPassword()}

        if getattr(aq_base(method), 'isDocTemp', 0):
            mail_text = method(self, self.REQUEST, **kw)
        else:
            mail_text = method(**kw)

        host = self.MailHost
        host.send( mail_text )

        return self.mail_password_response( self, REQUEST )

    security.declarePublic( 'registeredNotify' )
    def registeredNotify( self, new_member_id, password=None ):
        """ Handle mailing the registration / welcome message.
        """
        membership = getToolByName( self, 'portal_membership' )
        member = membership.getMemberById( new_member_id )

        if member is None:
            raise ValueError(_(u'The username you entered could not be '
                               u'found.'))

        if password is None:
            password = member.getPassword()

        email = member.getProperty( 'email' )

        if email is None:
            msg = _(u'No email address is registered for member: '
                    u'${member_id}', mapping={'member_id': new_member_id})
            raise ValueError(msg)

        check, msg = _checkEmail(email)
        if not check:
            raise ValueError(msg)

        # Rather than have the template try to use the mailhost, we will
        # render the message ourselves and send it from here (where we
        # don't need to worry about 'UseMailHost' permissions).
        method = getattr(self, 'member_registered_mail')
        kw = {'member': member, 'password': password, 'email': email}

        if getattr(aq_base(method), 'isDocTemp', 0):
            mail_text = method(self, self.REQUEST, **kw)
        else:
            mail_text = method(**kw)

        host = self.MailHost
        host.send( mail_text )

        return self.mail_password_response( self, self.REQUEST )

    security.declareProtected(ManagePortal, 'editMember')
    def editMember( self
                  , member_id
                  , properties=None
                  , password=None
                  , roles=None
                  , domains=None
                  ):
        """ Edit a user's properties and security settings

        o Checks should be done before this method is called using
          testPropertiesValidity and testPasswordValidity
        """

        mtool = getToolByName(self, 'portal_membership')
        member = mtool.getMemberById(member_id)
        member.setMemberProperties(properties)
        member.setSecurityProfile(password,roles,domains)

        return member

InitializeClass(RegistrationTool)

# See URL: http://www.zopelabs.com/cookbook/1033402597

_TESTS = ( ( re.compile("^[0-9a-zA-Z\.\-\_\+]+\@[0-9a-zA-Z\.\-]+$")
           , True
           , "Failed a"
           )
         , ( re.compile("^[^0-9a-zA-Z]|[^0-9a-zA-Z]$")
           , False
           , "Failed b"
           )
         , ( re.compile("([0-9a-zA-Z_]{1})\@.")
           , True
           , "Failed c"
           )
         , ( re.compile(".\@([0-9a-zA-Z]{1})")
           , True
           , "Failed d"
           )
         , ( re.compile(".\.\-.|.\-\..|.\.\..|.\-\-.")
           , False
           , "Failed e"
           )
         , ( re.compile(".\.\_.|.\-\_.|.\_\..|.\_\-.|.\_\_.")
           , False
           , "Failed f"
           )
         , ( re.compile(".\.([a-zA-Z]{2,3})$|.\.([a-zA-Z]{2,4})$")
           , True
           , "Failed g"
           )
         )

def _checkEmail( address ):
    for pattern, expected, message in _TESTS:
        matched = pattern.search( address ) is not None
        if matched != expected:
            return False, message
    return True, ''
