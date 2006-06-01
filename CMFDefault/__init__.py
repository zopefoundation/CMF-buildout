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
""" Default implementation of CMFCore.

$Id$
"""

import sys

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import initializeBasesPhase1
from Products.CMFCore.utils import initializeBasesPhase2
from Products.CMFCore.utils import ToolInit
from Products.CMFCore.utils import ContentInit
from Products.CMFCore.utils import registerIcon
from Products.GenericSetup import BASE
from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry

import factory
import utils
from permissions import AddPortalContent

import Portal
import Document
import Link
import NewsItem
import File
import Image
import Favorite
import SkinnedFolder

import DiscussionItem
import PropertiesTool
import MembershipTool
import MetadataTool
import RegistrationTool
import DublinCore
import DiscussionTool
import SyndicationTool
import DefaultWorkflow

contentClasses = ( Document.Document
                 , File.File
                 , Image.Image
                 , Link.Link
                 , Favorite.Favorite
                 , NewsItem.NewsItem
                 , SkinnedFolder.SkinnedFolder
                 )

contentConstructors = ( Document.addDocument
                      , File.addFile
                      , Image.addImage
                      , Link.addLink
                      , Favorite.addFavorite
                      , NewsItem.addNewsItem
                      , SkinnedFolder.addSkinnedFolder
                      )

bases = ( ( Portal.CMFSite
          , DublinCore.DefaultDublinCoreImpl
          , DiscussionItem.DiscussionItem
          )
          + contentClasses
        )

tools = ( DiscussionTool.DiscussionTool
        , MembershipTool.MembershipTool
        , RegistrationTool.RegistrationTool
        , PropertiesTool.PropertiesTool
        , MetadataTool.MetadataTool
        , SyndicationTool.SyndicationTool
        )

this_module = sys.modules[ __name__ ]

z_bases = initializeBasesPhase1( bases, this_module )
z_tool_bases = initializeBasesPhase1( tools, this_module )

# Make the skins available as DirectoryViews.
registerDirectory('skins', globals())
registerDirectory('help', globals())

def initialize( context ):

    initializeBasesPhase2( z_bases, context )
    initializeBasesPhase2( z_tool_bases, context )

    ToolInit( 'CMF Default Tool'
            , tools=tools
            , icon='tool.gif'
            ).initialize( context )

    # BBB: register oldstyle constructors
    ContentInit( 'CMF Default Content'
               , content_types=()
               , permission=AddPortalContent
               , extra_constructors=contentConstructors
               ).initialize( context )

    profile_registry.registerProfile('default',
                                     'CMFDefault Site',
                                     'Profile for a default CMFSite.',
                                     'profiles/default',
                                     'CMFDefault',
                                     BASE,
                                     for_=ISiteRoot,
                                    )

    profile_registry.registerProfile('sample_content',
                                     'Sample CMFDefault Content',
                                     'Content for a sample CMFSite.',
                                     'profiles/sample_content',
                                     'CMFDefault',
                                     EXTENSION,
                                     for_=ISiteRoot,
                                    )

    profile_registry.registerProfile('views_support',
                                     'Experimental CMFDefault Browser Views',
                                     'Hooks up the browser views.',
                                     'profiles/views_support',
                                     'CMFDefault',
                                     EXTENSION,
                                     for_=ISiteRoot,
                                    )

    context.registerClass( Portal.CMFSite
                         , constructors=(factory.addConfiguredSiteForm,
                                         factory.addConfiguredSite)
                         , icon='images/portal.gif'
                         )

    registerIcon( DefaultWorkflow.DefaultWorkflowDefinition
                , 'images/workflow.gif'
                , globals()
                )

    # make registerHelp work with 2 directories
    help = context.getProductHelp()
    lastRegistered = help.lastRegistered
    context.registerHelp(directory='help', clear=1)
    context.registerHelp(directory='interfaces', clear=1)
    if help.lastRegistered != lastRegistered:
        help.lastRegistered = None
        context.registerHelp(directory='help', clear=1)
        help.lastRegistered = None
        context.registerHelp(directory='interfaces', clear=0)
    context.registerHelpTitle('CMF Default Help')
