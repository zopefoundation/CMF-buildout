##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Five actions tool.

$Id$
"""

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Globals import DTMLFile
from OFS.SimpleItem import SimpleItem

from ActionInformation import ActionInformation
from ActionProviderBase import ActionProviderBase
from Expression import Expression
from permissions import ManagePortal
from utils import UniqueObject
from utils import _dtmldir

try:  # BBB (actually, FFF ;)
    from zope.app.publisher.browser.globalbrowsermenuservice import \
        globalBrowserMenuService
except ImportError:  # Zope3 > 3.0 loses services
    from zope.app import zapi
    from zope.app.publisher.interfaces.browser import IBrowserMenu
    from zope.app.publisher.browser.menu import getMenu

    def _listMenuIds():
        return zapi.getUtilitiesFor(IBrowserMenu)
else:

    from zope.app.browser.globalbrowsermenuservice import getMenu
    def _listMenuIds():
        return globalBrowserMenuService._registry.keys()


class FiveActionsTool(UniqueObject, SimpleItem, ActionProviderBase):
    """Five actions tool.

    Provides a bridge that makes Zope 3 menus available as CMF actions.
    """

    __implements__ = ActionProviderBase.__implements__

    id = 'portal_fiveactions'
    meta_type = 'CMF Five Actions Tool'

    security = ClassSecurityInfo()

    manage_options = (({'label': 'Overview',
                        'action': 'manage_overview'},
                       ) +
                      SimpleItem.manage_options)

    #
    # ZMI methods
    #

    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('explainFiveActionsTool', _dtmldir)

    #
    # ActionProvider
    #

    security.declarePrivate('listActions')
    def listActions(self, info=None, object=None):
        """ List all the actions defined by a provider.
        """
        if object is None and info is not None:
            # BBB (according to the interface)
            object = info.content
        if object is None:
            # The tool itself doesn't provide any action
            return ()

        actions = []

        for menu_id in _listMenuIds():
            for entry in getMenu(menu_id, object, self.REQUEST):
                # The action needs a unique name, so we'll build one
                # from the object_id and the action url. That is sure
                # to be unique.
                action = str(entry['action'])
                if object is None:
                    act_id = 'action_%s' % action
                else:
                    act_id = 'action_%s_%s' % (object.getId(), action)

                if entry['filter'] is None:
                    filter = None
                else:
                    filter = Expression(text=str(entry['filter']))

                act = ActionInformation(id=act_id,
                    title=str(entry['title']),
                    action=Expression(text='string:%s' % action),
                    condition=filter,
                    category=str(menu_id),
                    visible=1)
                actions.append(act)

        return tuple(actions)


InitializeClass(FiveActionsTool)
