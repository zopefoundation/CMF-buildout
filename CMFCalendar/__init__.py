##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMF Calendar product.

$Id$
"""

import utils
from Products.CMFCore import utils
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.DirectoryView import registerDirectory
from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry

import Event
import CalendarTool
from permissions import AddPortalContent


contentConstructors = (Event.addEvent,)
tools = ( CalendarTool.CalendarTool, )

# Make the skins available as DirectoryViews
registerDirectory('skins', globals())

def initialize(context):

    utils.ToolInit('CMF Calendar Tool', tools=tools, icon='tool.gif',
                   ).initialize( context )

    # BBB: register oldstyle constructors
    utils.ContentInit( 'CMF Calendar Content'
                     , content_types=()
                     , permission=AddPortalContent
                     , extra_constructors=contentConstructors
                     ).initialize( context )

    profile_registry.registerProfile('default',
                                     'CMFCalendar',
                                     'Adds calendar support.',
                                     'profiles/default',
                                     'CMFCalendar',
                                     EXTENSION,
                                     for_=ISiteRoot,
                                    )

    profile_registry.registerProfile('views_support',
                                     'Experimental CMFCalendar Browser Views',
                                     'Hooks up the browser views.',
                                     'profiles/views_support',
                                     'CMFCalendar',
                                     EXTENSION,
                                     for_=ISiteRoot,
                                    )
