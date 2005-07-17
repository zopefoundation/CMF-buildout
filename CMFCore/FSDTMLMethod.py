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
""" Customizable DTML methods that come from the filesystem.

$Id$
"""

from string import split
from os import path, stat

import Globals
from AccessControl import ClassSecurityInfo, getSecurityManager, Permissions
from OFS.DTMLMethod import DTMLMethod, decapitate, guess_content_type
from AccessControl.Role import RoleManager

from utils import _dtmldir
from CMFCorePermissions import View
from CMFCorePermissions import ViewManagementScreens
from CMFCorePermissions import FTPAccess
from DirectoryView import registerFileExtension, registerMetaType, expandpath
from FSObject import FSObject

try:
    # Zope 2.4.x
    from AccessControl.DTML import RestrictedDTML
except ImportError:
    class RestrictedDTML: pass

from OFS.Cache import Cacheable

_marker = []  # Create a new marker object.

class FSDTMLMethod(RestrictedDTML, RoleManager, FSObject, Globals.HTML):
    """FSDTMLMethods act like DTML methods but are not directly
    modifiable from the management interface."""

    meta_type = 'Filesystem DTML Method'

    manage_options=(
        (
            {'label':'Customize', 'action':'manage_main'},
            {'label':'View', 'action':'',
             'help':('OFSP','DTML-DocumentOrMethod_View.stx')},
            {'label':'Proxy', 'action':'manage_proxyForm',
             'help':('OFSP','DTML-DocumentOrMethod_Proxy.stx')},
            )
            +Cacheable.manage_options
        )

    _proxy_roles=()
    _cache_namespace_keys=()

    # Use declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = Globals.DTMLFile('custdtml', _dtmldir)

    _reading = 0

    def __init__(self, id, filepath, fullname=None, properties=None):
        FSObject.__init__(self, id, filepath, fullname, properties)
        # Normally called via HTML.__init__ but we don't need the rest that
        # happens there.
        self.initvars(None, {})

    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        return DTMLMethod(self.read(), __name__=self.getId())

    def _readFile(self, reparse):
        fp = expandpath(self._filepath)
        file = open(fp, 'rb')
        try:
            data = file.read()
        finally:
            file.close()
        self.raw = data
        if reparse:
            self._reading = 1  # Avoid infinite recursion
            try:
                self.cook()
            finally:
                self._reading = 0

    # Hook up chances to reload in debug mode
    security.declarePrivate('read_raw')
    def read_raw(self):
        if not self._reading:
            self._updateFromFS()
        return Globals.HTML.read_raw(self)

    #### The following is mainly taken from OFS/DTMLMethod.py ###
        
    index_html=None # Prevent accidental acquisition

    # Documents masquerade as functions:
    func_code = DTMLMethod.func_code

    default_content_type = 'text/html'

    def __call__(self, client=None, REQUEST={}, RESPONSE=None, **kw):
        """Render the document given a client object, REQUEST mapping,
        Response, and key word arguments."""

        self._updateFromFS()

        if not self._cache_namespace_keys:
            data = self.ZCacheable_get(default=_marker)
            if data is not _marker:
                # Return cached results.
                return data

        kw['document_id']   =self.getId()
        kw['document_title']=self.title

        security=getSecurityManager()
        security.addContext(self)
        try:
        
            if client is None:
                # Called as subtemplate, so don't need error propagation!
                r=apply(Globals.HTML.__call__, (self, client, REQUEST), kw)
                if RESPONSE is None: result = r
                else: result = decapitate(r, RESPONSE)
                if not self._cache_namespace_keys:
                    self.ZCacheable_set(result)
                return result

            r=apply(Globals.HTML.__call__, (self, client, REQUEST), kw)
            if type(r) is not type('') or RESPONSE is None:
                if not self._cache_namespace_keys:
                    self.ZCacheable_set(r)
                return r

        finally: security.removeContext(self)

        have_key=RESPONSE.headers.has_key
        if not (have_key('content-type') or have_key('Content-Type')):
            if self.__dict__.has_key('content_type'):
                c=self.content_type
            else:
                c, e=guess_content_type(self.getId(), r)
            RESPONSE.setHeader('Content-Type', c)
        result = decapitate(r, RESPONSE)
        if not self._cache_namespace_keys:
            self.ZCacheable_set(result)
        return result

    def getCacheNamespaceKeys(self):
        '''
        Returns the cacheNamespaceKeys.
        '''
        return self._cache_namespace_keys
        
    def setCacheNamespaceKeys(self, keys, REQUEST=None):
        '''
        Sets the list of names that should be looked up in the
        namespace to provide a cache key.
        '''
        ks = []
        for key in keys:
            key = strip(str(key))
            if key:
                ks.append(key)
        self._cache_namespace_keys = tuple(ks)
        if REQUEST is not None:
            return self.ZCacheable_manage(self, REQUEST)

    # Zope 2.3.x way:
    def validate(self, inst, parent, name, value, md=None):
        return getSecurityManager().validate(inst, parent, name, value)

    security.declareProtected(FTPAccess, 'manage_FTPget')
    manage_FTPget = DTMLMethod.manage_FTPget

    security.declareProtected(ViewManagementScreens, 'PrincipiaSearchSource')
    PrincipiaSearchSource = DTMLMethod.PrincipiaSearchSource

    security.declareProtected(ViewManagementScreens, 'document_src')
    document_src = DTMLMethod.document_src

    security.declareProtected(ViewManagementScreens, 'manage_haveProxy')
    manage_haveProxy = DTMLMethod.manage_haveProxy

Globals.InitializeClass(FSDTMLMethod)

registerFileExtension('dtml', FSDTMLMethod)
registerMetaType('DTML Method', FSDTMLMethod)
