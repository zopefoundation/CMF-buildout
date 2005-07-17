##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Information about customizable actions.

$Id$
"""

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Acquisition import aq_base, aq_inner, aq_parent
from OFS.SimpleItem import SimpleItem

from Expression import Expression
from permissions import View
from utils import getToolByName


_unchanged = [] # marker

class ActionInformation( SimpleItem ):

    """ Represent a single selectable action.

    Actions generate links to views of content, or to specific methods
    of the site.  They can be filtered via their conditions.
    """
    _isActionInformation = 1
    __allow_access_to_unprotected_subobjects__ = 1

    security = ClassSecurityInfo()

    def __init__( self
                , id
                , title=''
                , description=''
                , category='object'
                , condition=''
                , permissions=()
                , priority=10
                , visible=1
                , action=''
                ):
        """ Set up an instance.
        """
        self.edit( id
                 , title
                 , description
                 , category
                 , condition
                 , permissions
                 , priority
                 , visible
                 , action
                 )
        
    security.declarePrivate('edit')
    def edit( self
            , id=_unchanged
            , title=_unchanged
            , description=_unchanged
            , category=_unchanged
            , condition=_unchanged
            , permissions=_unchanged
            , priority=_unchanged
            , visible=_unchanged
            , action=_unchanged
            ):
        """Edit the specified properties.
        """
        
        if id is not _unchanged:
            self.id = id
        if title is not _unchanged:
            self.title = title
        if description is not _unchanged:
            self.description = description
        if category is not _unchanged:
            self.category = category
        if condition is not _unchanged:
            if condition and isinstance(condition, basestring):
                condition = Expression(condition)
            self.condition = condition
        if permissions is not _unchanged:
            self.permissions = permissions
        if priority is not _unchanged:
            self.priority = priority
        if visible is not _unchanged:
            self.visible = visible
        if action is not _unchanged:
            if action and isinstance(action, basestring):
                action = Expression(action)
            self.setActionExpression(action)

    security.declareProtected( View, 'Title' )
    def Title(self):

        """ Return the Action title.
        """
        return self.title or self.getId()

    security.declareProtected( View, 'Description' )
    def Description( self ):

        """ Return a description of the action.
        """
        return self.description

    security.declarePrivate( 'testCondition' )
    def testCondition( self, ec ):

        """ Evaluate condition using context, 'ec', and return 0 or 1.
        """
        if self.condition:
            return self.condition(ec)
        else:
            return 1

    security.declarePublic( 'getAction' )
    def getAction( self, ec ):

        """ Compute the action using context, 'ec'; return a mapping of
            info about the action.
        """
        info = {}
        info['id'] = self.id
        info['name'] = self.Title()
        expr = self.getActionExpression()
        __traceback_info__ = (info['id'], info['name'], expr)
        action_obj = self._getActionObject()
        info['url'] = action_obj and action_obj( ec ) or ''
        info['permissions'] = self.getPermissions()
        info['category'] = self.getCategory()
        info['visible'] = self.getVisibility()
        return info

    security.declarePrivate( '_getActionObject' )
    def _getActionObject( self ):

        """ Find the action object, working around name changes.
        """
        action = getattr( self, 'action', None )

        if action is None:  # Forward compatibility, used to be '_action'
            action = getattr( self, '_action', None )
            if action is not None:
                self.action = self._action
                del self._action

        return action

    security.declarePublic( 'getActionExpression' )
    def getActionExpression( self ):

        """ Return the text of the TALES expression for our URL.
        """
        action = self._getActionObject()
        expr = action and action.text or ''
        if expr and isinstance(expr, basestring):
            if not expr.startswith('python:') and not expr.startswith('string:'):
                expr = 'string:${object_url}/%s' % expr
                self.action = Expression( expr )
        return expr

    security.declarePrivate( 'setActionExpression' )
    def setActionExpression(self, action):
        if action and isinstance(action, basestring):
            if not action.startswith('python:')  and not action.startswith('string:'):
                action = 'string:${object_url}/%s' % action
                action = Expression( action )
        self.action = action

    security.declarePublic( 'getCondition' )
    def getCondition(self):

        """ Return the text of the TALES expression for our condition.
        """
        return getattr( self, 'condition', None ) and self.condition.text or ''

    security.declarePublic( 'getPermissions' )
    def getPermissions( self ):

        """ Return the permission, if any, required to execute the action.

        Return an empty tuple if no permission is required.
        """
        return self.permissions

    security.declarePublic( 'getCategory' )
    def getCategory( self ):

        """ Return the category in which the action should be grouped.
        """
        return self.category or 'object'

    security.declarePublic( 'getVisibility' )
    def getVisibility( self ):

        """ Return whether the action should be visible in the CMF UI.
        """
        return self.visible

    security.declarePrivate( 'clone' )
    def clone( self ):

        """ Return a newly-created AI just like us.
        """
        return self.__class__( id=self.id
                             , title=self.title
                             , description=self.description
                             , category =self.category
                             , condition=self.getCondition()
                             , permissions=self.permissions
                             , priority =self.priority
                             , visible=self.visible
                             , action=self.getActionExpression()
                             )

InitializeClass( ActionInformation )


def getOAI(context, object=None):
    request = getattr(context, 'REQUEST', None)
    if request:
        cache = request.get('_oai_cache', None)
        if cache is None:
            request['_oai_cache'] = cache = {}
        info = cache.get( id(object), None )
    else:
        info = None
    if info is None:
        if object is None or not hasattr(object, 'aq_base'):
            folder = None
        else:
            folder = object
            # Search up the containment hierarchy until we find an
            # object that claims it's a folder.
            while folder is not None:
                if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
                    # found it.
                    break
                else:
                    folder = aq_parent(aq_inner(folder))
        info = oai(context, folder, object)
        if request:
            cache[ id(object) ] = info
    return info


class oai:
    #Provided for backwards compatability
    # Provides information that may be needed when constructing the list of
    # available actions.
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__( self, tool, folder, object=None ):
        self.portal = portal = aq_parent(aq_inner(tool))
        membership = getToolByName(tool, 'portal_membership')
        self.isAnonymous = membership.isAnonymousUser()
        self.user_id = membership.getAuthenticatedMember().getId()
        self.portal_url = portal.absolute_url()
        if folder is not None:
            self.folder_url = folder.absolute_url()
            self.folder = folder
        else:
            self.folder_url = self.portal_url
            self.folder = portal
        self.content = object
        if object is not None:
            self.content_url = object.absolute_url()
        else:
            self.content_url = None

    def __getitem__(self, name):
        # Mapping interface for easy string formatting.
        if name[:1] == '_':
            raise KeyError, name
        if hasattr(self, name):
            return getattr(self, name)
        raise KeyError, name
