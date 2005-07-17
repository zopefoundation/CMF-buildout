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

import os
from os import path as os_path
import re
import operator
from types import StringType

from ExtensionClass import Base
from Acquisition import aq_get, aq_inner, aq_parent

from AccessControl import ClassSecurityInfo
from AccessControl import ModuleSecurityInfo
from AccessControl import getSecurityManager
from AccessControl.Permission import Permission
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.Role import gather_permissions

from Globals import package_home
from Globals import InitializeClass
from Globals import HTMLFile
from Globals import ImageFile
from Globals import MessageDialog

from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from OFS.PropertySheets import PropertySheets
from OFS.misc_ import misc_ as misc_images
from OFS.misc_ import Misc_ as MiscImage
try:
    from OFS.ObjectManager import UNIQUE
except ImportError:
    UNIQUE = 2

import StructuredText
from StructuredText.HTMLWithImages import HTMLWithImages

_STXDWI = StructuredText.DocumentWithImages.__class__

security = ModuleSecurityInfo( 'Products.CMFCore.utils' )

security.declarePublic( 'getToolByName'
                      , 'cookString'
                      , 'tuplize'
                      , 'format_stx'
                      , 'keywordsplitter'
                      , 'normalize'
                      , 'expandpath'
                      , 'minimalpath'
                      )

security.declarePrivate( '_getAuthenticatedUser'
                       , '_checkPermission'
                       , '_verifyActionPermissions'
                       , '_getViewFor'
                       , '_limitGrantedRoles'
                       , '_mergedLocalRoles'
                       , '_modifyPermissionMappings'
                       , '_ac_inherited_permissions'
                       )

_dtmldir = os_path.join( package_home( globals() ), 'dtml' )


#
#   Simple utility functions, callable from restricted code.
#
_marker = []  # Create a new marker object.

def getToolByName(obj, name, default=_marker):

    """ Get the tool, 'toolname', by acquiring it.

    o Application code should use this method, rather than simply
      acquiring the tool by name, to ease forward migration (e.g.,
      to Zope3).
    """
    try:
        tool = aq_get(obj, name, default, 1)
    except AttributeError:
        if default is _marker:
            raise
        return default
    else:
        if tool is _marker:
            raise AttributeError, name
        return tool

def cookString(text):

    """ Make a Zope-friendly ID from 'text'.

    o Remove any spaces

    o Lowercase the ID.
    """
    rgx = re.compile(r'(^_|[^a-zA-Z0-9-_~\,\.])')
    cooked = re.sub(rgx, "",text).lower()
    return cooked

def tuplize( valueName, value ):

    """ Make a tuple from 'value'.

    o Use 'valueName' to generate appropriate error messages.
    """
    if type(value) == type(()):
        return value
    if type(value) == type([]):
        return tuple( value )
    if type(value) == type(''):
        return tuple( value.split() )
    raise ValueError, "%s of unsupported type" % valueName

#
#   Security utilities, callable only from unrestricted code.
#
def _getAuthenticatedUser( self ):
    return getSecurityManager().getUser()

def _checkPermission(permission, obj, StringType = type('')):
    roles = rolesForPermissionOn(permission, obj)
    if type(roles) is StringType:
        roles=[roles]
    if _getAuthenticatedUser( obj ).allowed( obj, roles ):
        return 1
    return 0

def _verifyActionPermissions(obj, action):
    pp = action.get('permissions', ())
    if not pp:
        return 1
    for p in pp:
        if _checkPermission(p, obj):
            return 1
    return 0

def _getViewFor(obj, view='view'):
    ti = obj.getTypeInfo()
    if ti is not None:
        actions = ti.getActions()
        for action in actions:
            if action.get('id', None) == view:
                if _verifyActionPermissions(obj, action):
                    return obj.restrictedTraverse(action['action'])
        # "view" action is not present or not allowed.
        # Find something that's allowed.
        for action in actions:
            if _verifyActionPermissions(obj, action):
                return obj.restrictedTraverse(action['action'])
        raise 'Unauthorized', ('No accessible views available for %s' %
                               '/'.join(obj.getPhysicalPath()))
    else:
        raise 'Not Found', ('Cannot find default view for "%s"' %
                            '/'.join(obj.getPhysicalPath()))


# If Zope ever provides a call to getRolesInContext() through
# the SecurityManager API, the method below needs to be updated.
def _limitGrantedRoles(roles, context, special_roles=()):
    # Only allow a user to grant roles already possessed by that user,
    # with the exception that all special_roles can also be granted.
    user = _getAuthenticatedUser(context)
    if user is None:
        user_roles = ()
    else:
        user_roles = user.getRolesInContext(context)
    if 'Manager' in user_roles:
        # Assume all other roles are allowed.
        return
    for role in roles:
        if role not in special_roles and role not in user_roles:
            raise 'Unauthorized', 'Too many roles specified.'

limitGrantedRoles = _limitGrantedRoles  # XXX: Deprecated spelling

def _mergedLocalRoles(object):
    """Returns a merging of object and its ancestors'
    __ac_local_roles__."""
    # Modified from AccessControl.User.getRolesInContext().
    merged = {}
    object = getattr(object, 'aq_inner', object)
    while 1:
        if hasattr(object, '__ac_local_roles__'):
            dict = object.__ac_local_roles__ or {}
            if callable(dict): dict = dict()
            for k, v in dict.items():
                if merged.has_key(k):
                    merged[k] = merged[k] + v
                else:
                    merged[k] = v
        if hasattr(object, 'aq_parent'):
            object=object.aq_parent
            object=getattr(object, 'aq_inner', object)
            continue
        if hasattr(object, 'im_self'):
            object=object.im_self
            object=getattr(object, 'aq_inner', object)
            continue
        break
    return merged

mergedLocalRoles = _mergedLocalRoles    # XXX: Deprecated spelling

def _ac_inherited_permissions(ob, all=0):
    # Get all permissions not defined in ourself that are inherited
    # This will be a sequence of tuples with a name as the first item and
    # an empty tuple as the second.
    d = {}
    perms = getattr(ob, '__ac_permissions__', ())
    for p in perms: d[p[0]] = None
    r = gather_permissions(ob.__class__, [], d)
    if all:
       if hasattr(ob, '_subobject_permissions'):
           for p in ob._subobject_permissions():
               pname=p[0]
               if not d.has_key(pname):
                   d[pname]=1
                   r.append(p)
       r = list(perms) + r
    return r

def _modifyPermissionMappings(ob, map):
    """
    Modifies multiple role to permission mappings.
    """
    # This mimics what AccessControl/Role.py does.
    # Needless to say, it's crude. :-(
    something_changed = 0
    perm_info = _ac_inherited_permissions(ob, 1)
    for name, settings in map.items():
        cur_roles = rolesForPermissionOn(name, ob)
        t = type(cur_roles)
        if t is StringType:
            cur_roles = [cur_roles]
        else:
            cur_roles = list(cur_roles)
        changed = 0
        for (role, allow) in settings.items():
            if not allow:
                if role in cur_roles:
                    changed = 1
                    cur_roles.remove(role)
            else:
                if role not in cur_roles:
                    changed = 1
                    cur_roles.append(role)
        if changed:
            data = ()  # The list of methods using this permission.
            for perm in perm_info:
                n, d = perm[:2]
                if n == name:
                    data = d
                    break
            p = Permission(name, data, ob)
            p.setRoles(tuple(cur_roles))
            something_changed = 1
    return something_changed

#
#   Base classes for tools
#
class ImmutableId(Base):

    """ Base class for objects which cannot be renamed.
    """
    def _setId(self, id):

        """ Never allow renaming!
        """
        if id != self.getId():
            raise MessageDialog(
                title='Invalid Id',
                message='Cannot change the id of this object',
                action ='./manage_main',)

class UniqueObject (ImmutableId):

    """ Base class for objects which cannot be "overridden" / shadowed.
    """
    __replaceable__ = UNIQUE


class SimpleItemWithProperties (PropertyManager, SimpleItem):
    """
    A common base class for objects with configurable
    properties in a fixed schema.
    """
    manage_options = (
        PropertyManager.manage_options
        + SimpleItem.manage_options)


    security = ClassSecurityInfo()
    security.declarePrivate(
        'manage_addProperty',
        'manage_delProperties',
        'manage_changePropertyTypes',
        )

    def manage_propertiesForm(self, REQUEST, *args, **kw):
        'An override that makes the schema fixed.'
        my_kw = kw.copy()
        my_kw['property_extensible_schema__'] = 0
        return apply(PropertyManager.manage_propertiesForm,
                     (self, self, REQUEST,) + args, my_kw)

    security.declarePublic('propertyLabel')
    def propertyLabel(self, id):
        """Return a label for the given property id
        """
        for p in self._properties:
            if p['id'] == id:
                return p.get('label', id)
        return id

InitializeClass( SimpleItemWithProperties )


#
#   "Omnibus" factory framework for tools.
#
class ToolInit:

    """ Utility class for generating the factories for several tools.
    """
    __name__ = 'toolinit'

    security = ClassSecurityInfo()
    security.declareObjectPrivate()     # equivalent of __roles__ = ()

    def __init__(self, meta_type, tools, product_name, icon):
        self.meta_type = meta_type
        self.tools = tools
        self.product_name = product_name
        self.icon = icon

    def initialize(self, context):
        # Add only one meta type to the folder add list.
        context.registerClass(
            meta_type = self.meta_type,
            # This is a little sneaky: we add self to the
            # FactoryDispatcher under the name "toolinit".
            # manage_addTool() can then grab it.
            constructors = (manage_addToolForm,
                            manage_addTool,
                            self,),
            icon = self.icon
            )

        for tool in self.tools:
            tool.__factory_meta_type__ = self.meta_type
            tool.icon = 'misc_/%s/%s' % (self.product_name, self.icon)

InitializeClass( ToolInit )


addInstanceForm = HTMLFile('dtml/addInstance', globals())

def manage_addToolForm(self, REQUEST):

    """ Show the add tool form.
    """
    # self is a FactoryDispatcher.
    toolinit = self.toolinit
    tl = []
    for tool in toolinit.tools:
        tl.append(tool.meta_type)
    return addInstanceForm(addInstanceForm, self, REQUEST,
                           factory_action='manage_addTool',
                           factory_meta_type=toolinit.meta_type,
                           factory_product_name=toolinit.product_name,
                           factory_icon=toolinit.icon,
                           factory_types_list=tl,
                           factory_need_id=0)

def manage_addTool(self, type, REQUEST=None):

    """ Add the tool specified by name.
    """
    # self is a FactoryDispatcher.
    toolinit = self.toolinit
    obj = None
    for tool in toolinit.tools:
        if tool.meta_type == type:
            obj = tool()
            break
    if obj is None:
        raise 'NotFound', type
    self._setObject(obj.getId(), obj)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


#
#   Now, do the same for creating content factories.
#
class ContentInit:

    """ Utility class for generating factories for several content types.
    """
    __name__ = 'contentinit'

    security = ClassSecurityInfo()
    security.declareObjectPrivate()

    def __init__( self
                , meta_type
                , content_types
                , permission=None
                , extra_constructors=()
                , fti=()
                ):
        self.meta_type = meta_type
        self.content_types = content_types
        self.permission = permission
        self.extra_constructors = extra_constructors
        self.fti = fti

    def initialize(self, context):
        # Add only one meta type to the folder add list.
        context.registerClass(
            meta_type = self.meta_type
            # This is a little sneaky: we add self to the
            # FactoryDispatcher under the name "contentinit".
            # manage_addContentType() can then grab it.
            , constructors = ( manage_addContentForm
                               , manage_addContent
                               , self
                               , ('factory_type_information', self.fti)
                               ) + self.extra_constructors
            , permission = self.permission
            )

        for ct in self.content_types:
            ct.__factory_meta_type__ = self.meta_type

InitializeClass( ContentInit )

def manage_addContentForm(self, REQUEST):

    """ Show the add content type form.
    """
    # self is a FactoryDispatcher.
    ci = self.contentinit
    tl = []
    for t in ci.content_types:
        tl.append(t.meta_type)
    return addInstanceForm(addInstanceForm, self, REQUEST,
                           factory_action='manage_addContent',
                           factory_meta_type=ci.meta_type,
                           factory_icon=None,
                           factory_types_list=tl,
                           factory_need_id=1)

def manage_addContent( self, id, type, REQUEST=None ):

    """ Add the content type specified by name.
    """
    # self is a FactoryDispatcher.
    contentinit = self.contentinit
    obj = None
    for content_type in contentinit.content_types:
        if content_type.meta_type == type:
            obj = content_type( id )
            break
    if obj is None:
        raise 'NotFound', type
    self._setObject( id, obj )
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


def initializeBasesPhase1(base_classes, module):

    """ Execute the first part of initialization of ZClass base classes.

    Stuffs a _ZClass_for_x class in the module for each base.
    """
    rval = []
    for base_class in base_classes:
        d={}
        zclass_name = '_ZClass_for_%s' % base_class.__name__
        exec 'class %s: pass' % zclass_name in d
        Z = d[ zclass_name ]
        Z.propertysheets = PropertySheets()
        Z._zclass_ = base_class
        Z.manage_options = ()
        Z.__module__ = module.__name__
        setattr( module, zclass_name, Z )
        rval.append(Z)
    return rval

def initializeBasesPhase2(zclasses, context):

    """ Finishes ZClass base initialization.
    
    o 'zclasses' is the list returned by initializeBasesPhase1().
    
    o 'context' is a ProductContext object.
    """
    for zclass in zclasses:
        context.registerZClass(zclass)

def registerIcon(klass, iconspec, _prefix=None):

    """ Make an icon available for a given class.

    o 'klass' is the class being decorated.

    o 'iconspec' is the path within the product where the icon lives.
    """
    modname = klass.__module__
    pid = modname.split('.')[1]
    name = os_path.split(iconspec)[1]
    klass.icon = 'misc_/%s/%s' % (pid, name)
    icon = ImageFile(iconspec, _prefix)
    icon.__roles__=None
    if not hasattr(misc_images, pid):
        setattr(misc_images, pid, MiscImage(pid, {}))
    getattr(misc_images, pid)[name]=icon

#
#   StructuredText handling.
#
#   XXX:    This section is mostly workarounds for things fixed in the
#           core, and should go away soon.
#

class CMFDocumentClass( StructuredText.DocumentWithImages.__class__ ):
    """
    Override DWI to get '_' into links, and also turn on inner/named links.
    """
    text_types = [
        'doc_named_link',
        'doc_inner_link',
        ] + _STXDWI.text_types
    
    _URL_AND_PUNC = r'([a-zA-Z0-9_\@\.\,\?\=\&\+\!\/\:\;\-\#\~]+)'
    def doc_href( self
                , s
                , expr1 = re.compile( _STXDWI._DQUOTEDTEXT
                                    + "(:)"
                                    + _URL_AND_PUNC
                                    + _STXDWI._SPACES
                                    ).search
                , expr2 = re.compile( _STXDWI._DQUOTEDTEXT
                                    + r'(\,\s+)'
                                    + _URL_AND_PUNC
                                    + _STXDWI._SPACES
                                    ).search
                ):
        return _STXDWI.doc_href( self, s, expr1, expr2 )

CMFDocumentClass = CMFDocumentClass()

class CMFHtmlWithImages( HTMLWithImages ):
    """ Special subclass of HTMLWithImages, overriding document() """

    def document(self, doc, level, output):
        """\
        HTMLWithImages.document renders full HTML (head, title, body).  For
        CMF Purposes, we don't want that.  We just want those nice juicy
        body parts perfectly rendered.
        """
        for c in doc.getChildNodes():
           getattr(self, self.element_types[c.getNodeName()])(c, level, output)

CMFHtmlWithImages = CMFHtmlWithImages()
            
def format_stx( text, level=1 ):
    """
        Render STX to HTML.
    """
    st = StructuredText.Basic( text )   # Creates the basic DOM
    if not st:                          # If it's an empty object
        return ""                       # return now or have errors!

    doc = CMFDocumentClass( st )
    html = CMFHtmlWithImages( doc, level )
    return html

_format_stx = format_stx    # XXX: Deprecated spelling

#
#   Metadata Keyword splitter utilities
#
KEYSPLITRE = re.compile(r'[,;]')

def keywordsplitter( headers
                   , names=('Subject', 'Keywords',)
                   , splitter=KEYSPLITRE.split
                   ):
    """ Split keywords out of headers, keyed on names.  Returns list.
    """
    out = []
    for head in names:
        keylist = splitter(headers.get(head, ''))
        keylist = map(lambda x: x.strip(), keylist)
        out.extend(filter(operator.truth, keylist))
    return out

#
#   Directory-handling utilities
#
def normalize(p):
    return os_path.abspath(os_path.normcase(os_path.normpath(p)))

normINSTANCE_HOME = normalize(INSTANCE_HOME)
normSOFTWARE_HOME = normalize(SOFTWARE_HOME)

separators = (os.sep, os.altsep)

def expandpath(p):
    # Converts a minimal path to an absolute path.
    p = os_path.normpath(p)
    if os_path.isabs(p):
        return p
    abs = os_path.join(normINSTANCE_HOME, p)
    if os_path.exists(abs):
        return abs
    return os_path.join(normSOFTWARE_HOME, p)

def minimalpath(p):
    # Trims INSTANCE_HOME or SOFTWARE_HOME from a path.
    p = os_path.abspath(p)
    abs = normalize(p)
    l = len(normINSTANCE_HOME)
    if abs[:l] != normINSTANCE_HOME:
        l = len(normSOFTWARE_HOME)
        if abs[:l] != normSOFTWARE_HOME:
            # Can't minimize.
            return p
    p = p[l:]
    while p[:1] in separators:
        p = p[1:]
    return p
