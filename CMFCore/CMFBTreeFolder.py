##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""CMFBTreeFolder

$Id$
"""

from AccessControl.SecurityInfo import ClassSecurityInfo
from Globals import InitializeClass
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base

from PortalFolder import PortalFolderBase


def manage_addCMFBTreeFolder(dispatcher, id, title='', REQUEST=None):
    """Adds a new BTreeFolder object with id *id*.
    """
    id = str(id)
    ob = CMFBTreeFolder(id)
    ob.title = str(title)
    dispatcher._setObject(id, ob)
    ob = dispatcher._getOb(id)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(ob.absolute_url() + '/manage_main' )


class CMFBTreeFolder(BTreeFolder2Base, PortalFolderBase):

    """BTree folder for CMF sites.
    """

    meta_type = 'CMF BTree Folder'
    security = ClassSecurityInfo()

    def __init__(self, id, title=''):
        PortalFolderBase.__init__(self, id, title)
        BTreeFolder2Base.__init__(self, id)

    def _checkId(self, id, allow_dup=0):
        PortalFolderBase._checkId(self, id, allow_dup)
        BTreeFolder2Base._checkId(self, id, allow_dup)

InitializeClass(CMFBTreeFolder)
