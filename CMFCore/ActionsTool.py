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

"""Basic action list tool.

$Id$
"""
__version__='$Revision$'[11:-2]


from utils import UniqueObject, _getAuthenticatedUser, _checkPermission
from utils import getToolByName, _dtmldir
import CMFCorePermissions
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile, package_home
from urllib import quote
from Acquisition import aq_base, aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from string import join

class ActionInformation:
    # Provides information that may be needed when constructing the list of
    # available actions.
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, tool, folder, object=None):
        self.portal = portal = aq_parent(aq_inner(tool))
        membership = getToolByName(tool, 'portal_membership')
        self.isAnonymous = membership.isAnonymousUser()
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


class ActionsTool (UniqueObject, SimpleItem):
    """
        Weave together the various sources of "actions" which are apropos
        to the current user and context.
    """
    id = 'portal_actions'
    meta_type = 'CMF Actions Tool'

    action_providers = ( 'portal_actions'
                       , 'portal_memberdata'
                       , 'portal_registration'
                       , 'portal_discussion'
                       , 'portal_membership'
                       , 'portal_workflow'
                       , 'portal_undo'
                       )

    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }
                     , 
                     ) + SimpleItem.manage_options

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainActionsTool', _dtmldir )


    #
    # Programmatically manipulate the list of action providers
    #

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'listActionProviders'
                             )
    def listActionProviders( self ):
       """ returns a sequence of action providers known by this tool """
       return self.action_providers

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'addActionProvider'
                             )
    def addActionProvider( self, provider_name ):
        """ add the name of a new action provider """
        if hasattr( self, provider_name ):
            p_old = self.action_providers
            p_new = p_old + ( provider_name, )
            self.action_providers = p_new

    security.declarePrivate('listActions')
    def listActions(self, info):
        """
        List actions available from this tool
        """
        actions = []
        folder_url = info.folder_url   
        content_url = info.content_url   
        if folder_url is not None: 
            actions.append(
                { 'id'            : 'foldercontents'
                , 'name'          : 'Folder contents'
                , 'url'           : folder_url + '/folder_contents'
                , 'permissions'   : ['List folder contents']
                , 'category'      : 'folder'
                })
        return actions

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'deleteActionProvider'
                             )
    def deleteActionProvider( self, provider_name ):
        """ remove an action provider """
        if provider_name in self.action_providers:
            p_old = list( self.action_providers )
            del p_old[p_old.index( provider_name)]
            self.action_providers = tuple( p_old )

    #
    #   'portal_actions' interface methods
    #
    security.declarePublic('listFilteredActionsFor')
    def listFilteredActionsFor(self, object=None):
        '''Gets all actions available to the user and returns a mapping
        containing user actions, object actions, and global actions.
        '''
        portal = aq_parent(aq_inner(self))
        if object is None or not hasattr(object, 'aq_base'):
            folder = portal
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

        info = ActionInformation(self, folder, object)

        actions = []
        # Include actions from specific tools.
        for provider_name in self.listActionProviders():
            provider = getattr(self, provider_name)
            a = provider.listActions(info)
            if a:
                actions.extend(list(a))

        # Include actions from object.
        if object is not None:
            base = aq_base(object)
            types_tool = getToolByName( self, 'portal_types' )
            ti = types_tool.getTypeInfo( object )
            if ti is not None:
                defs = ti.getActions()
                if defs:
                    c_url = info.content_url
                    for d in defs:
                        a = d['action']
                        if a:
                            url = c_url + '/' + a
                        else:
                            url = c_url
                        actions.append({
                            'id': d.get('id', None),
                            'name': d['name'],
                            'url': url,
                            'permissions': d['permissions'],
                            'category': d.get('category', 'object'),
                            'visible': d.get('visible', 1),
                            })
            if hasattr(base, 'listActions'):
                a = object.listActions(info)
                if a:
                    actions.extend(list(a))

        # Reorganize the actions by category,
        # filtering out disallowed actions.
        filtered_actions={'user':[],
                          'folder':[],
                          'object':[],
                          'global':[],
                          'workflow':[],
                          }
        for action in actions:
            category = action['category']
            permissions = action.get('permissions', None)
            visible = action.get('visible', 1)
            if not visible:
                continue
            verified = 0
            if not permissions:
                # This action requires no extra permissions.
                verified = 1
            else:
                if category in ('object', 'workflow') and object is not None:
                    context = object
                elif category == 'folder' and folder is not None:
                    context = folder
                else:
                    context = portal
                for permission in permissions:
                    # The user must be able to match at least one of
                    # the listed permissions.
                    if _checkPermission(permission, context):
                        verified = 1
                        break
            if verified:
                catlist = filtered_actions.get(category, None)
                if catlist is None:
                    filtered_actions[category] = catlist = []
                # If a bug occurs where actions appear more than once,
                # a little code right here can fix it.
                catlist.append(action)
        return filtered_actions

    # listFilteredActions() is an alias.
    security.declarePublic('listFilteredActions')
    listFilteredActions = listFilteredActionsFor

InitializeClass(ActionsTool)
