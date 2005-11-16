##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFDefault setup handlers.

$Id$
"""

from Products.CMFCore.utils import getToolByName

from exceptions import BadRequest


def importVarious(context):
    """ Import various settings.

    This provisional handler will be removed again as soon as full handlers
    are implemented for these steps.
    """
    site = context.getSite()

    # add custom skin folder
    stool = getToolByName(site, 'portal_skins')
    try:
        stool.manage_addProduct['OFSP'].manage_addFolder(id='custom')
    except BadRequest:
        return 'Various settings: Nothing to import.'

    site.manage_addProduct['OFSP'].manage_addUserFolder()
    site.manage_addPortalFolder('Members')
    site.Members.manage_addProduct['OFSP'].manage_addDTMLMethod('index_html',
                                        'Member list', '<dtml-return roster>')

    return 'Various settings imported.'
