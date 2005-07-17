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
""" News content object.

$Id$
"""

from Globals import InitializeClass
from Document import Document
from utils import parseHeadersBody

from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from AccessControl import ClassSecurityInfo
from Products.CMFCore.WorkflowCore import WorkflowAction

factory_type_information = (
  { 'id'             : 'News Item'
  , 'meta_type'      : 'News Item'
  , 'description'    : """\
News Items contain short text articles and carry a title as well as
an optional description.
"""
  , 'icon'           : 'newsitem_icon.gif'
  , 'product'        : 'CMFDefault'
  , 'factory'        : 'addNewsItem'
  , 'immediate_view' : 'metadata_edit_form'
  , 'actions'        : ( { 'id'            : 'view'
                         , 'name'          : 'View'
                         , 'action': 'string:${object_url}/newsitem_view'
                         , 'permissions'   : (View,)
                         }
                       , { 'id'            : 'edit'
                         , 'name'          : 'Edit'
                         , 'action': 'string:${object_url}/newsitem_edit_form'
                         , 'permissions'   : (ModifyPortalContent,)
                         }
                       , { 'id'            : 'metadata'
                         , 'name'          : 'Metadata'
                         , 'action': 'string:${object_url}/metadata_edit_form'
                         , 'permissions'   : (ModifyPortalContent,)
                         }
                       )
  }
,
)

def addNewsItem( self
               , id
               , title=''
               , description=''
               , text=''
               , text_format='html'
               ):
    """
        Add a NewsItem
    """
    o=NewsItem( id=id
              , title=title
              , description=description
              , text=text
              , text_format=text_format
              )
    self._setObject(id, o)

class NewsItem( Document ):
    """
        A News Item
    """

    __implements__ = Document.__implements__  # redundant, but explicit

    meta_type='News Item'
    text_format = 'html'

    security = ClassSecurityInfo()

    security.declareProtected(ModifyPortalContent, 'edit')
    def edit( self, text, description=None, text_format=None ):
        """
            Edit the News Item
        """
        if text_format is None:
            text_format = getattr(self, 'text_format', 'html')
        if description is not None:
            self.setDescription( description )
        Document.edit( self, text_format, text )


InitializeClass( NewsItem )

