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
""" PortalContent: Base class for all CMF content.

$Id$
"""

import string, urllib

from DateTime import DateTime
from Globals import InitializeClass
from Acquisition import aq_base
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo

from CMFCorePermissions import AccessContentsInformation, View, FTPAccess

from interfaces.Contentish import Contentish
from DynamicType import DynamicType
from utils import _checkPermission, _getViewFor

from CMFCatalogAware import CMFCatalogAware

try:
    from webdav.Lockable import ResourceLockedError
except ImportError:
    class ResourceLockedError( Exception ):
        pass

try: 
    from webdav.WriteLockInterface import WriteLockInterface
    NoWL = 0
except ImportError:
    NoWL = 1


class PortalContent(DynamicType, CMFCatalogAware, SimpleItem):
    """
        Base class for portal objects.
        
        Provides hooks for reviewing, indexing, and CMF UI.

        Derived classes must implement the interface described in
        interfaces/DublinCore.py.
    """
    
    if not NoWL:
        __implements__ = (WriteLockInterface, Contentish,)
    else:
        __implements__ = (Contentish)
    isPortalContent = 1
    _isPortalContent = 1  # More reliable than 'isPortalContent'.

    manage_options = ( ( { 'label'  : 'Dublin Core'
                         , 'action' : 'manage_metadata'
                         }
                       , { 'label'  : 'Edit'
                         , 'action' : 'manage_edit'
                         }
                       , { 'label'  : 'View'
                         , 'action' : 'view'
                         }
                       )
                     + CMFCatalogAware.manage_options
                     + SimpleItem.manage_options
                     )

    security = ClassSecurityInfo()

    security.declareObjectProtected(View)

    # The security for FTP methods aren't set up by default in our
    # superclasses...  :(
    security.declareProtected(FTPAccess,
                              'manage_FTPstat',
                              'manage_FTPget',
                              'manage_FTPlist',)

    def failIfLocked(self):
        """
        Check if isLocked via webDav
        """
        if self.wl_isLocked():
            raise ResourceLockedError, 'This resource is locked via webDAV'
        return 0

    # indexed methods
    # ---------------
    
    security.declareProtected(View, 'SearchableText')
    def SearchableText(self):
        "Returns a concatination of all searchable text"
        # Should be overriden by portal objects
        return "%s %s" % (self.Title(), self.Description())

    # Contentish interface methods
    # ----------------------------

    def __call__(self):
        '''
        Invokes the default view.
        '''
        view = _getViewFor(self)
        if getattr(aq_base(view), 'isDocTemp', 0):
            return apply(view, (self, self.REQUEST))
        else:
            return view()

    index_html = None  # This special value informs ZPublisher to use __call__

    security.declareProtected(View, 'view')
    def view(self):
        '''
        Returns the default view even if index_html is overridden.
        '''
        return self()

InitializeClass(PortalContent)
