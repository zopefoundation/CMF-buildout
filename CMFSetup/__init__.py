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
""" CMFSetup product initialization.

$Id$
"""

from AccessControl import ModuleSecurityInfo

from interfaces import BASE, EXTENSION
from permissions import ManagePortal
from registry import _profile_registry as profile_registry

security = ModuleSecurityInfo( 'Products.CMFSetup' )
security.declareProtected( ManagePortal, 'profile_registry' )

def initialize( context ):

    from Products.CMFCore.utils import ToolInit, registerIcon
    from tool import SetupTool


    ToolInit( 'CMF Setup Tool'
            , tools=[ SetupTool ]
            , icon='www/tool.png'
            ).initialize( context )

