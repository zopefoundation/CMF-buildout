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
""" Type registration tool.

$Id$
"""

from sys import exc_info
from warnings import warn
from xml.dom.minidom import parseString

import Products
from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from Acquisition import aq_base
from Acquisition import aq_get
from Globals import DTMLFile
from Globals import InitializeClass
from OFS.Folder import Folder
from OFS.ObjectManager import IFAwareObjectManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zLOG import LOG, ERROR
from zope.interface import implements
try:
    from zope.i18nmessageid import MessageFactory
except ImportError: # BBB
    from zope.i18nmessageid import MessageIDFactory as MessageFactory

def MessageID(val, domain): # XXX performance?
    return MessageFactory(domain)(val)

from Products.GenericSetup.interfaces import INodeImporter

from ActionProviderBase import ActionProviderBase
from exceptions import AccessControl_Unauthorized
from exceptions import BadRequest
from exceptions import zExceptions_Unauthorized
from interfaces import ITypeInformation
from interfaces import ITypesTool
from interfaces.portal_types \
        import ContentTypeInformation as z2ITypeInformation
from interfaces.portal_types import portal_types as z2ITypesTool
from permissions import AccessContentsInformation
from permissions import ManagePortal
from permissions import View
from utils import _checkPermission
from utils import _dtmldir
from utils import _wwwdir
from utils import cookString
from utils import getActionContext
from utils import getToolByName
from utils import SimpleItemWithProperties
from utils import UniqueObject


_marker = []  # Create a new marker.


class TypeInformation(SimpleItemWithProperties, ActionProviderBase):

    """
    Base class for information about a content type.
    """

    _isTypeInformation = 1

    manage_options = ( SimpleItemWithProperties.manage_options[:1]
                     + ( {'label':'Aliases',
                          'action':'manage_aliases'}, )
                     + ActionProviderBase.manage_options
                     + SimpleItemWithProperties.manage_options[1:]
                     )

    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'manage_editProperties')
    security.declareProtected(ManagePortal, 'manage_changeProperties')
    security.declareProtected(ManagePortal, 'manage_propertiesForm')

    _basic_properties = (
        {'id':'title', 'type': 'string', 'mode':'w',
         'label':'Title'},
        {'id':'description', 'type': 'text', 'mode':'w',
         'label':'Description'},
        {'id':'i18n_domain', 'type': 'string', 'mode':'w',
         'label':'I18n Domain'},
        {'id':'content_icon', 'type': 'string', 'mode':'w',
         'label':'Icon'},
        {'id':'content_meta_type', 'type': 'string', 'mode':'w',
         'label':'Product meta type'},
        )

    _advanced_properties = (
        {'id':'immediate_view', 'type': 'string', 'mode':'w',
         'label':'Initial view name'},
        {'id':'global_allow', 'type': 'boolean', 'mode':'w',
         'label':'Implicitly addable?'},
        {'id':'filter_content_types', 'type': 'boolean', 'mode':'w',
         'label':'Filter content types?'},
        {'id':'allowed_content_types'
         , 'type': 'multiple selection'
         , 'mode':'w'
         , 'label':'Allowed content types'
         , 'select_variable':'listContentTypes'
         },
        { 'id': 'allow_discussion', 'type': 'boolean', 'mode': 'w'
          , 'label': 'Allow Discussion?'
          },
        )

    title = ''
    description = ''
    i18n_domain = ''
    content_meta_type = ''
    content_icon = ''
    immediate_view = ''
    filter_content_types = True
    allowed_content_types = ()
    allow_discussion = False
    global_allow = True

    def __init__(self, id, **kw):

        self.id = id

        if not kw:
            return

        kw = kw.copy()  # Get a modifiable dict.

        if (not kw.has_key('content_meta_type')
            and kw.has_key('meta_type')):
            kw['content_meta_type'] = kw['meta_type']

        if (not kw.has_key('content_icon')
            and kw.has_key('icon')):
            kw['content_icon'] = kw['icon']

        self.manage_changeProperties(**kw)

        actions = kw.get( 'actions', () )
        # make sure we have a copy
        _actions = []
        for action in actions:
            _actions.append( action.copy() )
        actions = tuple(_actions)
        # We don't know if actions need conversion, so we always add oldstyle
        # _actions and convert them.
        self._actions = actions
        self._convertActions()

        aliases = kw.get( 'aliases', _marker )
        if aliases is _marker:
            self._guessMethodAliases()
        else:
            self.setMethodAliases(aliases)

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_aliases')
    manage_aliases = PageTemplateFile( 'typeinfoAliases.zpt', _wwwdir )

    security.declareProtected(ManagePortal, 'manage_setMethodAliases')
    def manage_setMethodAliases(self, REQUEST):
        """ Config method aliases.
        """
        form = REQUEST.form
        aliases = {}
        for k, v in form['aliases'].items():
            v = v.strip()
            if v:
                aliases[k] = v

        _dict = {}
        for k, v in form['methods'].items():
            if aliases.has_key(k):
                _dict[ aliases[k] ] = v
        self.setMethodAliases(_dict)
        REQUEST.RESPONSE.redirect('%s/manage_aliases' % self.absolute_url())

    #
    #   Accessors
    #
    security.declareProtected(View, 'Title')
    def Title(self):
        """
            Return the "human readable" type name (note that it
            may not map exactly to the 'portal_type', e.g., for
            l10n/i18n or where a single content class is being
            used twice, under different names.
        """
        if self.title and self.i18n_domain:
            return MessageID(self.title, self.i18n_domain)
        else:
            return self.title or self.getId()

    security.declareProtected(View, 'Description')
    def Description(self):
        """
            Textual description of the class of objects (intended
            for display in a "constructor list").
        """
        if self.description and self.i18n_domain:
            return MessageID(self.description, self.i18n_domain)
        else:
            return self.description

    security.declareProtected(View, 'Metatype')
    def Metatype(self):
        """
            Returns the Zope 'meta_type' for this content object.
            May be used for building the list of portal content
            meta types.
        """
        return self.content_meta_type

    security.declareProtected(View, 'getIcon')
    def getIcon(self):
        """
            Returns the icon for this content object.
        """
        return self.content_icon

    security.declarePublic('allowType')
    def allowType( self, contentType ):
        """
            Can objects of 'contentType' be added to containers whose
            type object we are?
        """
        if not self.filter_content_types:
            ti = self.getTypeInfo( contentType )
            if ti is None or ti.globalAllow():
                return 1

        #If a type is enabled to filter and no content_types are allowed
        if not self.allowed_content_types:
            return 0

        if contentType in self.allowed_content_types:
            return 1

        # Backward compatibility for code that expected Type() to work.
        for ti in self.listTypeInfo():
            if ti.Title() == contentType:
                return ti.getId() in self.allowed_content_types

        return 0

    security.declarePublic('getId')
    def getId(self):
        return self.id

    security.declarePublic('allowDiscussion')
    def allowDiscussion( self ):
        """
            Can this type of object support discussion?
        """
        return self.allow_discussion

    security.declarePublic('globalAllow')
    def globalAllow(self):
        """
        Should this type be implicitly addable anywhere?
        """
        return self.global_allow

    security.declarePublic('listActions')
    def listActions(self, info=None, object=None):
        """ Return a sequence of the action info objects for this type.
        """
        if self._actions and isinstance(self._actions[0], dict):
            self._convertActions()

        return self._actions or ()

    security.declarePrivate( '_convertActions' )
    def _convertActions( self ):
        """ Upgrade dictionary-based actions.
        """
        aa, self._actions = self._actions, ()

        for action in aa:

            # Some backward compatibility stuff.
            if not 'id' in action:
                action['id'] = cookString(action['name'])

            if not 'title' in action:
                action['title'] = action.get('name', action['id'].capitalize())

            # historically, action['action'] is simple string
            actiontext = action.get('action').strip() or 'string:${object_url}'
            if actiontext[:7] not in ('python:', 'string:'):
                actiontext = 'string:${object_url}/%s' % actiontext

            self.addAction(
                  id=action['id']
                , name=action['title']
                , action=actiontext
                , condition=action.get('condition')
                , permission=action.get( 'permissions', () )
                , category=action.get('category', 'object')
                , visible=action.get('visible', True)
                )

    security.declarePublic('constructInstance')
    def constructInstance(self, container, id, *args, **kw):
        """Build an instance of the type.

        Builds the instance in 'container', using 'id' as its id.
        Returns the object.
        """
        if not self.isConstructionAllowed(container):
            raise AccessControl_Unauthorized('Cannot create %s' % self.getId())

        ob = self._constructInstance(container, id, *args, **kw)

        return self._finishConstruction(ob)

    security.declarePrivate('_finishConstruction')
    def _finishConstruction(self, ob):
        """
            Finish the construction of a content object.
            Set its portal_type, insert it into the workflows.
        """
        if hasattr(ob, '_setPortalTypeName'):
            ob._setPortalTypeName(self.getId())

        if hasattr(aq_base(ob), 'notifyWorkflowCreated'):
            ob.notifyWorkflowCreated()

        ob.reindexObject()
        return ob

    security.declareProtected(ManagePortal, 'getMethodAliases')
    def getMethodAliases(self):
        """ Get method aliases dict.
        """
        if not hasattr(self, '_aliases'):
            self._guessMethodAliases()
        aliases = self._aliases
        # for aliases created with CMF 1.5.0beta
        for key, method_id in aliases.items():
            if isinstance(method_id, tuple):
                aliases[key] = method_id[0]
                self._p_changed = True
        return aliases.copy()

    security.declareProtected(ManagePortal, 'setMethodAliases')
    def setMethodAliases(self, aliases):
        """ Set method aliases dict.
        """
        _dict = {}
        for k, v in aliases.items():
            v = v.strip()
            if v:
                _dict[ k.strip() ] = v
        if not getattr(self, '_aliases', None) == _dict:
            self._aliases = _dict
            return True
        else:
            return False

    security.declarePublic('queryMethodID')
    def queryMethodID(self, alias, default=None, context=None):
        """ Query method ID by alias.
        """
        if not hasattr(self, '_aliases'):
            self._guessMethodAliases()
        aliases = self._aliases
        method_id = aliases.get(alias, default)
        # for aliases created with CMF 1.5.0beta
        if isinstance(method_id, tuple):
            method_id = method_id[0]
        return method_id

    security.declarePrivate('_guessMethodAliases')
    def _guessMethodAliases(self):
        """ Guess and set Method Aliases. Used for upgrading old TIs.
        """
        context = getActionContext(self)
        actions = self.listActions()
        ordered = []
        _dict = {}
        viewmethod = ''

        # order actions and search 'mkdir' action
        for action in actions:
            if action.getId() == 'view':
                ordered.insert(0, action)
            elif action.getId() == 'mkdir':
                try:
                    mkdirmethod = action.action(context).strip()
                except AttributeError:
                    continue
                if mkdirmethod.startswith('/'):
                    mkdirmethod = mkdirmethod[1:]
                _dict['mkdir'] = mkdirmethod
            else:
                ordered.append(action)

        # search 'view' action
        for action in ordered:
            perms = action.getPermissions()
            if not perms or View in perms:
                try:
                    viewmethod = action.action(context).strip()
                except (AttributeError, TypeError):
                    break
                if viewmethod.startswith('/'):
                    viewmethod = viewmethod[1:]
                if not viewmethod:
                    viewmethod = '(Default)'
                break
        else:
            viewmethod = '(Default)'
        if viewmethod:
            _dict['view'] = viewmethod

        # search default action
        for action in ordered:
            try:
                defmethod = action.action(context).strip()
            except (AttributeError, TypeError):
                break
            if defmethod.startswith('/'):
                defmethod = defmethod[1:]
            if not defmethod:
                break
        else:
            if viewmethod:
                _dict['(Default)'] = viewmethod

        # correct guessed values if we know better
        if self.content_meta_type in ('Portal File', 'Portal Folder',
                                      'Portal Image'):
            _dict['(Default)'] = 'index_html'
            if viewmethod == '(Default)':
                _dict['view'] = 'index_html'
        if self.content_meta_type in ('Document', 'News Item'):
            _dict['gethtml'] = 'source_html'

        self.setMethodAliases(_dict)
        return 1

InitializeClass( TypeInformation )


class FactoryTypeInformation(TypeInformation):

    """
    Portal content factory.
    """

    implements(ITypeInformation)
    __implements__ = z2ITypeInformation

    meta_type = 'Factory-based Type Information'
    security = ClassSecurityInfo()

    _properties = (TypeInformation._basic_properties + (
        {'id':'product', 'type': 'string', 'mode':'w',
         'label':'Product name'},
        {'id':'factory', 'type': 'string', 'mode':'w',
         'label':'Product factory method'},
        ) + TypeInformation._advanced_properties)

    product = ''
    factory = ''

    #
    #   Agent methods
    #
    def _getFactoryMethod(self, container, check_security=1):
        if not self.product or not self.factory:
            raise ValueError, ('Product factory for %s was undefined' %
                               self.getId())
        p = container.manage_addProduct[self.product]
        m = getattr(p, self.factory, None)
        if m is None:
            raise ValueError, ('Product factory for %s was invalid' %
                               self.getId())
        if not check_security:
            return m
        if getSecurityManager().validate(p, p, self.factory, m):
            return m
        raise AccessControl_Unauthorized( 'Cannot create %s' % self.getId() )

    def _queryFactoryMethod(self, container, default=None):

        if not self.product or not self.factory or container is None:
            return default

        # In case we aren't wrapped.
        dispatcher = getattr(container, 'manage_addProduct', None)

        if dispatcher is None:
            return default

        try:
            p = dispatcher[self.product]
        except AttributeError:
            LOG('Types Tool', ERROR, '_queryFactoryMethod raised an exception',
                error=exc_info())
            return default

        m = getattr(p, self.factory, None)

        if m:
            try:
                # validate() can either raise Unauthorized or return 0 to
                # mean unauthorized.
                if getSecurityManager().validate(p, p, self.factory, m):
                    return m
            except zExceptions_Unauthorized:  # Catch *all* Unauths!
                pass

        return default

    security.declarePublic('isConstructionAllowed')
    def isConstructionAllowed( self, container ):
        """
        a. Does the factory method exist?

        b. Is the factory method usable?

        c. Does the current user have the permission required in
        order to invoke the factory method?
        """
        m = self._queryFactoryMethod(container)
        return (m is not None)

    security.declarePrivate('_constructInstance')
    def _constructInstance(self, container, id, *args, **kw):
        """Build a bare instance of the appropriate type.

        Does not do any security checks.

        Returns the object without calling _finishConstruction().
        """
        m = self._getFactoryMethod(container, check_security=0)

        id = str(id)

        if getattr(aq_base(m), 'isDocTemp', 0):
            kw['id'] = id
            newid = m(m.aq_parent, self.REQUEST, *args, **kw)
        else:
            newid = m(id, *args, **kw)
        # allow factory to munge ID
        newid = newid or id

        return container._getOb(newid)

InitializeClass( FactoryTypeInformation )


class ScriptableTypeInformation( TypeInformation ):

    """
    Invokes a script rather than a factory to create the content.
    """

    implements(ITypeInformation)
    __implements__ = z2ITypeInformation

    meta_type = 'Scriptable Type Information'
    security = ClassSecurityInfo()

    _properties = (TypeInformation._basic_properties + (
        {'id':'permission', 'type': 'string', 'mode':'w',
         'label':'Constructor permission'},
        {'id':'constructor_path', 'type': 'string', 'mode':'w',
         'label':'Constructor path'},
        ) + TypeInformation._advanced_properties)

    permission = ''
    constructor_path = ''

    #
    #   Agent methods
    #
    security.declarePublic('isConstructionAllowed')
    def isConstructionAllowed( self, container ):
        """
        Does the current user have the permission required in
        order to construct an instance?
        """
        permission = self.permission
        if permission and not _checkPermission( permission, container ):
            return 0
        return 1

    security.declarePrivate('_constructInstance')
    def _constructInstance(self, container, id, *args, **kw):
        """Build a bare instance of the appropriate type.

        Does not do any security checks.

        Returns the object without calling _finishConstruction().
        """
        constructor = self.restrictedTraverse( self.constructor_path )

        # make sure ownership is explicit before switching the context
        if not hasattr( aq_base(constructor), '_owner' ):
            constructor._owner = aq_get(constructor, '_owner')
        #   Rewrap to get into container's context.
        constructor = aq_base(constructor).__of__( container )

        id = str(id)
        return constructor(container, id, *args, **kw)

InitializeClass( ScriptableTypeInformation )


_addTypeInfo_template = PageTemplateFile('addTypeInfo.zpt', _wwwdir)

def manage_addFactoryTIForm(dispatcher, REQUEST):
    """ Get the add form for factory-based type infos.
    """
    template = _addTypeInfo_template.__of__(dispatcher)
    meta_type = FactoryTypeInformation.meta_type
    return template(add_meta_type=meta_type,
                    profiles=_getProfileInfo(dispatcher, meta_type))

def manage_addScriptableTIForm(dispatcher, REQUEST):
    """ Get the add form for scriptable type infos.
    """
    template = _addTypeInfo_template.__of__(dispatcher)
    meta_type = ScriptableTypeInformation.meta_type
    return template(add_meta_type=meta_type,
                    profiles=_getProfileInfo(dispatcher, meta_type))

def _getProfileInfo(dispatcher, meta_type):
    profiles = []
    stool = getToolByName(dispatcher, 'portal_setup', None)
    if stool:
        for info in stool.listContextInfos():
            type_ids = []
            context = stool._getImportContext(info['id'])
            filenames = context.listDirectory('types')
            if filenames is None:
                continue
            for filename in filenames:
                body = context.readDataFile(filename, subdir='types')
                if body is None:
                    continue
                root = parseString(body).documentElement
                if root.getAttribute('meta_type') == meta_type:
                    type_id = root.getAttribute('name')
                    type_ids.append(type_id)
            if not type_ids:
                continue
            type_ids.sort()
            profiles.append({'id': info['id'],
                             'title': info['title'],
                             'type_ids': tuple(type_ids)})
    return tuple(profiles)

def manage_addTypeInfo(dispatcher, add_meta_type, id, settings_id='',
                       REQUEST=None):
    """Add a new TypeInformation object of type 'add_meta_type' with ID 'id'.
    """
    settings_node = None
    if settings_id:
        stool = getToolByName(dispatcher, 'portal_setup', None)
        if stool:
            profile_id, type_id = settings_id.split('/')
            context = stool._getImportContext(profile_id)
            filenames = context.listDirectory('types')
            for filename in filenames or ():
                body = context.readDataFile(filename, subdir='types')
                if body is not None:
                    root = parseString(body).documentElement
                    if root.getAttribute('name') != type_id:
                        continue
                    if root.getAttribute('meta_type') == add_meta_type:
                        settings_node = root
                        if not id:
                            id = type_id
                        break
    for mt in Products.meta_types:
        if mt['name'] == add_meta_type:
            klass = mt['instance']
            break
    else:
        raise ValueError('Meta type %s is not a type class.' % add_meta_type)
    obj = klass(id)
    if settings_node:
        INodeImporter(obj).importNode(settings_node)
    dispatcher._setObject(id, obj)

    if REQUEST:
        return dispatcher.manage_main(dispatcher, REQUEST)

allowedTypes = [
    'Script (Python)',
    'Python Method',
    'DTML Method',
    'External Method',
    ]


class TypesTool(UniqueObject, IFAwareObjectManager, Folder,
                ActionProviderBase):

    """
        Provides a configurable registry of portal content types.
    """

    implements(ITypesTool)
    __implements__ = (z2ITypesTool, ActionProviderBase.__implements__)

    id = 'portal_types'
    meta_type = 'CMF Types Tool'
    _product_interfaces = (ITypeInformation,)

    security = ClassSecurityInfo()

    manage_options = ( Folder.manage_options[:1]
                     + ( {'label':'Aliases',
                          'action':'manage_aliases'}, )
                     + ActionProviderBase.manage_options
                     + ( {'label':'Overview',
                          'action':'manage_overview'}, )
                     + Folder.manage_options[1:]
                     )

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile( 'explainTypesTool', _dtmldir )

    security.declareProtected(ManagePortal, 'manage_aliases')
    manage_aliases = PageTemplateFile( 'typesAliases.zpt', _wwwdir )

    #
    #   ObjectManager methods
    #
    def all_meta_types(self):
        # this is a workaround and should be removed again if allowedTypes
        # have an interface we can use in _product_interfaces
        all = TypesTool.inheritedAttribute('all_meta_types')(self)
        others = [ mt for mt in Products.meta_types
                   if mt['name'] in allowedTypes ]
        return tuple(all) + tuple(others)

    #
    #   other methods
    #
    security.declareProtected(ManagePortal, 'manage_addTypeInformation')
    def manage_addTypeInformation(self, add_meta_type, id=None,
                                  typeinfo_name=None, RESPONSE=None):
        """Create a TypeInformation in self.
        """
        # BBB: typeinfo_name is ignored
        if not id:
            raise BadRequest('An id is required.')
        for mt in Products.meta_types:
            if mt['name'] == add_meta_type:
                klass = mt['instance']
                break
        else:
            raise ValueError, (
                'Meta type %s is not a type class.' % add_meta_type)
        id = str(id)
        ob = klass(id)
        self._setObject(id, ob)
        if RESPONSE is not None:
            RESPONSE.redirect('%s/manage_main' % self.absolute_url())

    security.declareProtected(ManagePortal, 'manage_setTIMethodAliases')
    def manage_setTIMethodAliases(self, REQUEST):
        """ Config method aliases.
        """
        form = REQUEST.form
        aliases = {}
        for k, v in form['aliases'].items():
            v = v.strip()
            if v:
                aliases[k] = v

        for ti in self.listTypeInfo():
            _dict = {}
            for k, v in form[ ti.getId() ].items():
                if aliases.has_key(k):
                    _dict[ aliases[k] ] = v
            ti.setMethodAliases(_dict)
        REQUEST.RESPONSE.redirect('%s/manage_aliases' % self.absolute_url())

    security.declareProtected(AccessContentsInformation, 'getTypeInfo')
    def getTypeInfo( self, contentType ):
        """
            Return an instance which implements the
            TypeInformation interface, corresponding to
            the specified 'contentType'.  If contentType is actually
            an object, rather than a string, attempt to look up
            the appropriate type info using its portal_type.
        """
        if not isinstance(contentType, basestring):
            if hasattr(aq_base(contentType), 'getPortalTypeName'):
                contentType = contentType.getPortalTypeName()
                if contentType is None:
                    return None
            else:
                return None
        ob = getattr( self, contentType, None )
        if getattr(aq_base(ob), '_isTypeInformation', 0):
            return ob
        else:
            return None

    security.declareProtected(AccessContentsInformation, 'listTypeInfo')
    def listTypeInfo( self, container=None ):
        """
            Return a sequence of instances which implement the
            TypeInformation interface, one for each content
            type registered in the portal.
        """
        rval = []
        for t in self.objectValues():
            # Filter out things that aren't TypeInformation and
            # types for which the user does not have adequate permission.
            if not getattr(aq_base(t), '_isTypeInformation', 0):
                continue
            if not t.getId():
                # XXX What's this used for ?
                # Not ready.
                continue
            # check we're allowed to access the type object
            if container is not None:
                if not t.isConstructionAllowed(container):
                    continue
            rval.append(t)
        return rval

    security.declareProtected(AccessContentsInformation, 'listContentTypes')
    def listContentTypes(self, container=None, by_metatype=0):
        """ List type info IDs.

        Passing 'by_metatype' is deprecated (type information may not
        correspond 1:1 to an underlying meta_type). This argument will be
        removed when CMFCore/dtml/catalogFind.dtml doesn't need it anymore.
        """
        typenames = {}
        for t in self.listTypeInfo( container ):

            if by_metatype:
                warn('TypeInformation.listContentTypes(by_metatype=1) is '
                     'deprecated.',
                     DeprecationWarning)
                name = t.Metatype()
            else:
                name = t.getId()

            if name:
                typenames[ name ] = None

        result = typenames.keys()
        result.sort()
        return result

    security.declarePublic('constructContent')
    def constructContent( self
                        , type_name
                        , container
                        , id
                        , RESPONSE=None
                        , *args
                        , **kw
                        ):
        """
            Build an instance of the appropriate content class in
            'container', using 'id'.
        """
        info = self.getTypeInfo( type_name )
        if info is None:
            raise ValueError('No such content type: %s' % type_name)

        ob = info.constructInstance(container, id, *args, **kw)

        if RESPONSE is not None:
            immediate_url = '%s/%s' % ( ob.absolute_url()
                                      , info.immediate_view )
            RESPONSE.redirect( immediate_url )

        return ob.getId()

    security.declarePrivate( 'listActions' )
    def listActions(self, info=None, object=None):
        """ List all the actions defined by a provider.
        """
        actions = list( self._actions )

        if object is None and info is not None:
            object = info.object
        if object is not None:
            type_info = self.getTypeInfo(object)
            if type_info is not None:
                actions.extend( type_info.listActions() )

        return actions

    security.declareProtected(ManagePortal, 'listMethodAliasKeys')
    def listMethodAliasKeys(self):
        """ List all defined method alias names.
        """
        _dict = {}
        for ti in self.listTypeInfo():
            aliases = ti.getMethodAliases()
            for k, v in aliases.items():
                _dict[k] = 1
        rval = _dict.keys()
        rval.sort()
        return rval

InitializeClass( TypesTool )
