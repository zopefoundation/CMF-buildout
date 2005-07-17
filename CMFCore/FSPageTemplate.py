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
##########################################################################
"""Customizable page templates that come from the filesystem.

$Id$
"""

from string import split, replace
from os import stat
import re, sys

import Globals, Acquisition
from DateTime import DateTime
from DocumentTemplate.DT_Util import html_quote
from Acquisition import aq_parent
from AccessControl import getSecurityManager, ClassSecurityInfo
from Shared.DC.Scripts.Script import Script
from Products.PageTemplates.PageTemplate import PageTemplate
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate, Src

from DirectoryView import registerFileExtension, registerMetaType, expandpath
from CMFCorePermissions import ViewManagementScreens
from CMFCorePermissions import View
from CMFCorePermissions import FTPAccess
from FSObject import FSObject
from utils import getToolByName, _setCacheHeaders

xml_detect_re = re.compile('^\s*<\?xml\s+')

from OFS.Cache import Cacheable

_marker = []  # Create a new marker object.

class FSPageTemplate(FSObject, Script, PageTemplate):
    "Wrapper for Page Template"
     
    meta_type = 'Filesystem Page Template'

    _owner = None  # Unowned

    manage_options=(
        (
            {'label':'Customize', 'action':'manage_main'},
            {'label':'Test', 'action':'ZScriptHTML_tryForm'},
            )
            +Cacheable.manage_options
        ) 

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = Globals.DTMLFile('dtml/custpt', globals())

    # Declare security for unprotected PageTemplate methods.
    security.declarePrivate('pt_edit', 'write')

    def __init__(self, id, filepath, fullname=None, properties=None):
        FSObject.__init__(self, id, filepath, fullname, properties)
        self.ZBindings_edit(self._default_bindings)

    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        obj = ZopePageTemplate(self.getId(), self._text, self.content_type)
        obj.expand = 0
        obj.write(self.read())
        return obj

#    def ZCacheable_isCachingEnabled(self):
#        return 0

    def _readFile(self, reparse):
        fp = expandpath(self._filepath)
        file = open(fp, 'r')    # not 'rb', as this is a text file!
        try: 
            data = file.read()
        finally: 
            file.close()
        if reparse:
            if xml_detect_re.match(data):
                # Smells like xml
                self.content_type = 'text/xml'
            else:
                try:
                    del self.content_type
                except (AttributeError, KeyError):
                    pass
            self.write(data)

    security.declarePrivate('read')
    def read(self):
        # Tie in on an opportunity to auto-update
        self._updateFromFS()
        return FSPageTemplate.inheritedAttribute('read')(self)

    ### The following is mainly taken from ZopePageTemplate.py ###

    expand = 0

    func_defaults = None
    func_code = ZopePageTemplate.func_code
    _default_bindings = ZopePageTemplate._default_bindings

    security.declareProtected(View, '__call__')

    def pt_macros(self):
        # Tie in on an opportunity to auto-reload
        self._updateFromFS()
        return FSPageTemplate.inheritedAttribute('pt_macros')(self)

    def pt_render(self, source=0, extra_context={}):
        self._updateFromFS()  # Make sure the template has been loaded.
        try:
            result = FSPageTemplate.inheritedAttribute('pt_render')(
                                    self, source, extra_context
                                    )
            if not source:
                _setCacheHeaders(self, extra_context)
            return result

        except RuntimeError:
            if Globals.DevelopmentMode:
                err = FSPageTemplate.inheritedAttribute( 'pt_errors' )( self )
                if not err:
                    err = sys.exc_info()
                err_type = err[0]
                err_msg = '<pre>%s</pre>' % replace( str(err[1]), "\'", "'" )
                msg = 'FS Page Template %s has errors: %s.<br>%s' % (
                    self.id, err_type, html_quote(err_msg) )
                raise RuntimeError, msg
            else:
                raise
                
    security.declarePrivate( '_ZPT_exec' )
    _ZPT_exec = ZopePageTemplate._exec

    security.declarePrivate( '_exec' )
    def _exec(self, bound_names, args, kw):
        """Call a FSPageTemplate"""
        try:
            response = self.REQUEST.RESPONSE
        except AttributeError:
            response = None
        # Read file first to get a correct content_type default value.
        self._updateFromFS()
        
        if not kw.has_key('args'):
            kw['args'] = args
        bound_names['options'] = kw

        try:
            response = self.REQUEST.RESPONSE
            if not response.headers.has_key('content-type'):
                response.setHeader('content-type', self.content_type)
        except AttributeError:
            pass
            
        security=getSecurityManager()
        bound_names['user'] = security.getUser()

        # Retrieve the value from the cache.
        keyset = None
        if self.ZCacheable_isCachingEnabled():
            # Prepare a cache key.
            keyset = {
                      # Why oh why?
                      # All this code is cut and paste
                      # here to make sure that we 
                      # dont call _getContext and hence can't cache
                      # Annoying huh?
                      'here': self.aq_parent.getPhysicalPath(),
                      'bound_names': bound_names}
            result = self.ZCacheable_get(keywords=keyset)
            if result is not None:
                # Got a cached value.
                return result

        # Execute the template in a new security context.
        security.addContext(self)
        try:
            result = self.pt_render(extra_context=bound_names)
            if keyset is not None:
                # Store the result in the cache.
                self.ZCacheable_set(result, keywords=keyset)
            return result
        finally:
            security.removeContext(self)
        
        return result
 
    # Copy over more methods
    security.declareProtected(FTPAccess, 'manage_FTPget')
    manage_FTPget = ZopePageTemplate.manage_FTPget

    security.declareProtected(View, 'get_size')
    get_size = ZopePageTemplate.get_size
    getSize = get_size

    security.declareProtected(ViewManagementScreens, 'PrincipiaSearchSource')
    PrincipiaSearchSource = ZopePageTemplate.PrincipiaSearchSource

    security.declareProtected(ViewManagementScreens, 'document_src')
    document_src = ZopePageTemplate.document_src

    pt_getContext = ZopePageTemplate.pt_getContext

    ZScriptHTML_tryParams = ZopePageTemplate.ZScriptHTML_tryParams


d = FSPageTemplate.__dict__
d['source.xml'] = d['source.html'] = Src()

Globals.InitializeClass(FSPageTemplate)

registerFileExtension('pt', FSPageTemplate)
registerFileExtension('zpt', FSPageTemplate)
registerFileExtension('html', FSPageTemplate)
registerFileExtension('htm', FSPageTemplate)
registerMetaType('Page Template', FSPageTemplate)

