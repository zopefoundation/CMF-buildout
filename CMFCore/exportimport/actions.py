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

$Id$
"""

from zope.app import zapi

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import PURGE, UPDATE
from Products.GenericSetup.utils import I18NURI
from Products.GenericSetup.utils import NodeAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase

from Products.CMFCore.interfaces import IAction
from Products.CMFCore.interfaces import IActionCategory
from Products.CMFCore.interfaces import IActionProvider
from Products.CMFCore.interfaces import IActionsTool
from Products.CMFCore.interfaces.portal_actions \
        import ActionProvider as z2IActionProvider
from Products.CMFCore.utils import getToolByName

_FILENAME = 'actions.xml'
_SPECIAL_PROVIDERS = ('portal_actions', 'portal_types', 'portal_workflow')


class ActionCategoryNodeAdapter(NodeAdapterBase, ObjectManagerHelpers,
                                PropertyManagerHelpers):

    """Node im- and exporter for ActionCategory.
    """

    __used_for__ = IActionCategory

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractObjects())
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        if mode == PURGE:
            self._purgeProperties()
            self._purgeObjects()

        self._initProperties(node, mode)
        self._initObjects(node, mode)


class ActionNodeAdapter(NodeAdapterBase, PropertyManagerHelpers):

    """Node im- and exporter for Action.
    """

    __used_for__ = IAction

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        if mode == PURGE:
            self._purgeProperties()

        self._initProperties(node, mode)


class ActionsToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers):

    """XML im- and exporter for ActionsTool.
    """

    __used_for__ = IActionsTool

    _LOGGER_ID = 'actions'

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._getObjectNode('object')
        node.setAttribute('xmlns:i18n', I18NURI)
        node.appendChild(self._extractProviders())
        node.appendChild(self._extractObjects())

        self._logger.info('Actions tool exported.')
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        if mode == PURGE:
            self._purgeProviders()
            self._purgeObjects()

        self._initObjects(node, mode)
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

            if provider_id in _SPECIAL_PROVIDERS and \
                    provider_id not in self.context.listActionProviders():
                self.context.addActionProvider(provider_id)

            # BBB: for CMF 1.5 profiles
            self._initOldstyleActions(child, mode)

    def _initOldstyleActions(self, node, mode):
        # BBB: for CMF 1.5 profiles
        doc = node.ownerDocument
        fragment = doc.createDocumentFragment()
        for child in node.childNodes:
            if child.nodeName != 'action':
                continue

            parent = fragment
            for category_id in child.getAttribute('category').split('/'):
                newnode = doc.createElement('object')
                newnode.setAttribute('name', str(category_id))
                newnode.setAttribute('meta_type', 'CMF Action Category')
                parent.appendChild(newnode)
                parent = newnode
            newnode = doc.createElement('object')
            newnode.setAttribute('name', str(child.getAttribute('action_id')))
            newnode.setAttribute('meta_type', 'CMF Action')

            mapping = {'title': 'title',
                       'url_expr': 'url_expr',
                       'condition_expr': 'available_expr',
                       'visible': 'visible'}
            for old, new in mapping.iteritems():
                newchild = doc.createElement('property')
                newchild.setAttribute('name', new)
                newsub = doc.createTextNode(child.getAttribute(old))
                newchild.appendChild(newsub)
                newnode.appendChild(newchild)

            newchild = doc.createElement('property')
            newchild.setAttribute('name', 'permissions')
            for sub in child.childNodes:
                if sub.nodeName == 'permission':
                    newsub = doc.createElement('element')
                    newsub.setAttribute('value', self._getNodeText(sub))
                    newchild.appendChild(newsub)
            newnode.appendChild(newchild)

            parent.appendChild(newnode)

        self._initObjects(fragment, UPDATE)


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
