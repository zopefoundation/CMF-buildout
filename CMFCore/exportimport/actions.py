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
"""Actions tool node adapters.

$Id: actions.py 39947 2005-11-06 16:41:15Z yuppie $
"""

from zope.app import zapi

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import PURGE
from Products.GenericSetup.utils import XMLAdapterBase

from Products.CMFCore.interfaces import IActionProvider
from Products.CMFCore.interfaces import IActionsTool
from Products.CMFCore.interfaces.portal_actions \
        import ActionProvider as z2IActionProvider
from Products.CMFCore.utils import getToolByName

_FILENAME = 'actions.xml'


class ActionsToolXMLAdapter(XMLAdapterBase):

    """XML im- and exporter for ActionsTool.
    """

    __used_for__ = IActionsTool

    _LOGGER_ID = 'actions'

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._getObjectNode('object')
        node.appendChild(self._extractProviders())

        self._logger.info('Actions tool exported.')
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        if mode == PURGE:
            self._purgeProviders()

        self._initProviders(node, mode)

        self._logger.info('Actions tool imported.')

    def _extractProviders(self):
        fragment = self._doc.createDocumentFragment()
        for provider_id in self.context.listActionProviders():
            child = self._doc.createElement('action-provider')
            child.setAttribute('name', provider_id)
            # BBB: for CMF 1.5 profiles
            sub = self._extractOldstyleActions(provider_id)
            child.appendChild(sub)
            fragment.appendChild(child)
        return fragment

    def _extractOldstyleActions(self, provider_id):
        # BBB: for CMF 1.5 profiles
        fragment = self._doc.createDocumentFragment()

        provider = getToolByName(self.context, provider_id)
        if not (IActionProvider.providedBy(provider) or
                z2IActionProvider.isImplementedBy(provider)):
            return fragment

        if provider_id == 'portal_actions':
            actions = provider._actions
        else:
            actions = provider.listActions()

        if actions and isinstance(actions[0], dict):
            return fragment

        for ai in actions:
            mapping = ai.getMapping()
            child = self._doc.createElement('action')
            child.setAttribute('action_id', mapping['id'])
            child.setAttribute('category', mapping['category'])
            child.setAttribute('condition_expr', mapping['condition'])
            child.setAttribute('title', mapping['title'])
            child.setAttribute('url_expr', mapping['action'])
            child.setAttribute('visible', str(mapping['visible']))
            for permission in mapping['permissions']:
                sub = self._doc.createElement('permission')
                sub.appendChild(self._doc.createTextNode(permission))
                child.appendChild(sub)
            fragment.appendChild(child)
        return fragment

    def _purgeProviders(self):
        for provider_id in self.context.listActionProviders():
            self.context.deleteActionProvider(provider_id)

    def _initProviders(self, node, mode):
        for child in node.childNodes:
            if child.nodeName != 'action-provider':
                continue

            provider_id = str(child.getAttribute('name'))
            if not provider_id:
                # BBB: for CMF 1.5 profiles
                provider_id = str(child.getAttribute('id'))
            if child.hasAttribute('remove'):
                if provider_id in self.context.listActionProviders():
                    self.context.deleteActionProvider(provider_id)
                continue

            if provider_id not in self.context.listActionProviders():
                self.context.addActionProvider(provider_id)

            # delete any actions that are auto-created
            provider = getToolByName(self.context, provider_id)
            num_actions = len(provider.listActions())
            if num_actions:
                provider.deleteActions(range(0,num_actions))

            # BBB: for CMF 1.5 profiles
            self._initOldstyleActions(child, mode)

    def _initOldstyleActions(self, node, mode):
        # BBB: for CMF 1.5 profiles
        provider_id = str(node.getAttribute('name'))
        if not provider_id:
            provider_id = str(node.getAttribute('id'))
        provider = getToolByName(self.context, provider_id)
        for child in node.childNodes:
            if child.nodeName != 'action':
                continue

            action_id = str(child.getAttribute('action_id'))
            title = str(child.getAttribute('title'))
            url_expr = str(child.getAttribute('url_expr'))
            condition_expr = str(child.getAttribute('condition_expr'))
            category = str(child.getAttribute('category'))
            visible = str(child.getAttribute('visible'))
            if visible.lower() == 'true':
                visible = 1
            else:
                visible = 0

            permission = ''
            for permNode in child.childNodes:
                if permNode.nodeName == 'permission':
                    for textNode in permNode.childNodes:
                        if textNode.nodeName != '#text' or \
                               not textNode.nodeValue.strip():
                            continue
                        permission = str(textNode.nodeValue)
                        break  # only one permission is allowed
                    if permission:
                        break

            provider.addAction(action_id, title, url_expr,
                               condition_expr, permission,
                               category, visible)


def importActionProviders(context):
    """Import actions tool.
    """
    site = context.getSite()
    logger = context.getLogger('actions')
    tool = getToolByName(site, 'portal_actions')

    body = context.readDataFile(_FILENAME)
    if body is None:
        logger.info('Nothing to import.')
        return

    importer = zapi.queryMultiAdapter((tool, context), IBody)
    if importer is None:
        logger.warning('Import adapter misssing.')
        return

    importer.body = body

def exportActionProviders(context):
    """Export actions tool.
    """
    site = context.getSite()
    logger = context.getLogger('actions')
    tool = getToolByName(site, 'portal_actions', None)
    if tool is None:
        logger.info('Nothing to export.')
        return

    exporter = zapi.queryMultiAdapter((tool, context), IBody)
    if exporter is None:
        logger.warning('Export adapter misssing.')
        return

    context.writeDataFile(_FILENAME, exporter.body, exporter.mime_type)
