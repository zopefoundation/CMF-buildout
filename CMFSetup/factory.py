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
""" Configured site factory implementation.

$Id$
"""

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.Portal import CMFSite

from interfaces import EXTENSION
from registry import _profile_registry as profile_registry
from tool import SetupTool
from utils import _wwwdir

def addConfiguredSiteForm( dispatcher ):

    """ Wrap the PTF in 'dispatcher', including 'profile_registry' in options.
    """
    wrapped = PageTemplateFile( 'siteAddForm', _wwwdir ).__of__( dispatcher )

    base_profiles = []
    extension_profiles = []

    for info in profile_registry.listProfileInfo():
        if info.get('type') == EXTENSION:
            extension_profiles.append(info)
        else:
            base_profiles.append(info)

    return wrapped( base_profiles=tuple(base_profiles),
                    extension_profiles =tuple(extension_profiles) )

def addConfiguredSite( dispatcher
                     , site_id
                     , profile_id
                     , snapshot=True
                     , RESPONSE=None 
                     , extension_ids=()
                     ):

    """ Add a CMFSite to 'dispatcher', configured according to 'profile_id'.
    """
    site = CMFSite( site_id )
    dispatcher._setObject( site_id, site )
    site = dispatcher._getOb( site_id )

    setup_tool = SetupTool()
    site._setObject( 'portal_setup', setup_tool )
    setup_tool = getToolByName( site, 'portal_setup' )

    setup_tool.setImportContext( 'profile-%s' % profile_id )
    setup_tool.runAllImportSteps()
    for extension_id in extension_ids:
        setup_tool.setImportContext( 'profile-%s' % extension_id )
        setup_tool.runAllImportSteps()
    setup_tool.setImportContext( 'profile-%s' % profile_id )

    if snapshot is True:
        setup_tool.createSnapshot( 'initial_configuration' )

    if RESPONSE is not None:
        RESPONSE.redirect( '%s/manage_main?update_menu=1'
                         % dispatcher.absolute_url() )
