##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
 
"""
This module implements a portal-managed File class.  It is based on
Zope's built-in File object, but modifies the behaviour slightly to
make it more Portal-friendly.
"""

ADD_CONTENT_PERMISSION = 'Add portal content'


from Globals import HTMLFile, HTML
from Products.CMFCore.PortalContent import PortalContent
import Globals
from DublinCore import DefaultDublinCoreImpl

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.WorkflowCore import WorkflowAction, afterCreate


factory_type_information = ( { 'id'             : 'File'
                             , 'meta_type'      : 'Portal File'
                             , 'description'    : """\
File objects can contain arbitrary downloadable files."""
                             , 'icon'           : 'file_icon.gif'
                             , 'product'        : 'CMFDefault'
                             , 'factory'        : 'addFile'
                             , 'immediate_view' : 'metadata_edit_form'
                             , 'actions'        :
                                ( { 'name'          : 'View'
                                  , 'action'        : 'file_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'name'          : 'Download'
                                  , 'action'        : ''
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'name'          : 'Edit'
                                  , 'action'        : 'file_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'name'          : 'Metadata'
                                  , 'action'        : 'metadata_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                )
                             }
                           ,
                           )

import OFS.Image

def addFile( self
           , id
           , title=''
           , file=''
           , content_type=''
           , precondition=''
           , subject=()
           , description=''
           , contributors=()
           , effective_date=None
           , expiration_date=None
           , format='text/html'
           , language=''
           , rights=''
           ):
    """
    Add a File
    """

    # cookId sets the id and title if they are not explicity specified
    id, title = OFS.Image.cookId(id, title, file)

    self=self.this()

    # Instantiate the object and set its description.
    fobj = File( id, title, '', content_type, precondition, subject
               , description, contributors, effective_date, expiration_date
               , format, language, rights
               )
    
    # Add the File instance to self
    self._setObject(id, fobj)

    # 'Upload' the file.  This is done now rather than in the
    # constructor because the object is now in the ZODB and
    # can span ZODB objects.
    self._getOb(id).manage_upload(file)

    afterCreate(self._getOb(id))


class File( OFS.Image.File
          , PortalContent
          , DefaultDublinCoreImpl
          ):
    """
        A Portal-managed File
    """

    # The order of base classes is very significant in this case.
    # Image.File does not store it's id in it's 'id' attribute.
    # Rather, it has an 'id' method which returns the contents of the
    # instnace's __name__ attribute.  Inheriting in the other order
    # obscures this method, resulting in much pulling of hair and
    # gnashing of teeth and fraying of nerves.  Don't do it.
    #
    # Really.
    # 
    # Note that if you use getId() to retrieve an object's ID, you will avoid
    # this problem altogether. getId is the new way, accessing .id is
    # deprecated.
    
    meta_type='Portal File'
    effective_date = expiration_date = None
    _isDiscussable = 1
    icon = PortalContent.icon

    __ac_permissions__ = (
        (CMFCorePermissions.View, ('download',)),
        (CMFCorePermissions.ModifyPortalContent, ('edit',)),
        )
    
    def __init__( self
                , id
                , title=''
                , file=''
                , content_type=''
                , precondition=''
                , subject=()
                , description=''
                , contributors=()
                , effective_date=None
                , expiration_date=None
                , format='text/html'
                , language='en-US'
                , rights=''
                ):
        OFS.Image.File.__init__( self, id, title, file
                               , content_type, precondition )
        DefaultDublinCoreImpl.__init__( self, title, subject, description
                               , contributors, effective_date, expiration_date
                               , format, language, rights )
    
    def SearchableText(self):
        """
        SeachableText is used for full text seraches of a portal.  It
        should return a concatenation of all useful text.
        """
        return "%s %s" % (self.title, self.description)

    def manage_afterAdd(self, item, container):
        """Both of my parents have an afterAdd method"""
        OFS.Image.File.manage_afterAdd(self, item, container)
        PortalContent.manage_afterAdd(self, item, container)

    def manage_beforeDelete(self, item, container):
        """Both of my parents have a beforeDelete method"""
        PortalContent.manage_beforeDelete(self, item, container)
        OFS.Image.File.manage_beforeDelete(self, item, container)

    def _isNotEmpty(self, file):
        """ Do various checks on 'file' to try to determine non emptiness. """
        if not file:
            return 0                    # Catches None, Missing.Value, ''
        elif file and (type(file) is type('')):
            return 1
        elif getattr(file, 'filename', None):
            return 1
        elif not hasattr(file, 'read'):
            return 0
        else:
            file.seek(0,2)              # 0 bytes back from end of file
            t = file.tell()             # Report the location
            file.seek(0)                # and return pointer back to 0
            if t: return 1
            else: return 0

    def edit(self, precondition='', file=''):
        """ Perform changes for user """
        if precondition: self.precondition = precondition
        elif self.precondition: del self.precondition

        if self._isNotEmpty(file):
            self.manage_upload(file)

        self.setFormat(self.content_type)
    edit = WorkflowAction(edit)

    def download(self, REQUEST, RESPONSE):
        """Download this item.
        
        Calls OFS.Image.File.index_html to perform the actual transfer after
        first setting Content-Disposition to suggest a filename.
        
        This method is deprecated, use the URL of this object itself. Because
        the default view of a File object is to download, rather than view,
        this method is obsolete. Also note that certain browsers do not deal
        well with a Content-Disposition header.

        """

        RESPONSE.setHeader('Content-Disposition',
                           'attachment; filename=%s' % self.getId())
        return OFS.Image.File.index_html(self, REQUEST, RESPONSE)

Globals.default__class_init__(File)

