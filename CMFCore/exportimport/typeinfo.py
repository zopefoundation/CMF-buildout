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
"""Types tool xml adapters and setup handlers.

$Id$
"""

from xml.dom.minidom import parseString

import Products
from zope.app import zapi

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import PURGE
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import I18NURI
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase

from Products.CMFCore.interfaces import ITypeInformation
from Products.CMFCore.interfaces import ITypesTool
from Products.CMFCore.utils import getToolByName


_FILENAME = 'typestool.xml'


class TypeInformationXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):

    """Node im- and exporter for TypeInformation.
    """

    __used_for__ = ITypeInformation

    _LOGGER_ID = 'typestool'

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._getObjectNode('object')
        node.setAttribute('xmlns:i18n', I18NURI)
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractAliases())
        node.appendChild(self._extractActions())

        self._logger.info('\'%s\' type info exported.' % self.context.getId())
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        if mode == PURGE:
            self._purgeProperties()
            self._purgeAliases()
            self._purgeActions()

        self._initOldstyleProperties(node, mode)
        self._initProperties(node, mode)
        self._initAliases(node, mode)
        self._initActions(node, mode)

        self._logger.info('\'%s\' type info imported.' % self.context.getId())

    def _extractAliases(self):
        fragment = self._doc.createDocumentFragment()
        aliases = self.context.getMethodAliases().items()
        aliases.sort()
        for k, v in aliases:
            child = self._doc.createElement('alias')
            child.setAttribute('from', k)
            child.setAttribute('to', v)
            fragment.appendChild(child)
        return fragment

    def _purgeAliases(self):
        self.context.setMethodAliases({})

    def _initAliases(self, node, mode):
        aliases = self.context.getMethodAliases()
        for child in node.childNodes:
            # BBB: for CMF 1.5 profiles
            #      'alias' nodes moved one level up.
            if child.nodeName == 'aliases':
                for sub in child.childNodes:
                    if sub.nodeName != 'alias':
                        continue
                    k = str(sub.getAttribute('from'))
                    v = str(sub.getAttribute('to'))
                    aliases[k] = v

            if child.nodeName != 'alias':
                continue
            k = str(child.getAttribute('from'))
            v = str(child.getAttribute('to'))
            aliases[k] = v
        self.context.setMethodAliases(aliases)

    def _extractActions(self):
        fragment = self._doc.createDocumentFragment()
        actions = self.context.listActions()
        for ai in actions:
            ai_info = ai.getMapping()
            child = self._doc.createElement('action')
            child.setAttribute('title', ai_info['title'])
            child.setAttribute('action_id', ai_info['id'])
            child.setAttribute('category', ai_info['category'])
            child.setAttribute('condition_expr', ai_info['condition'])
            child.setAttribute('url_expr', ai_info['action'])
            child.setAttribute('visible', str(bool(ai_info['visible'])))
            for permission in ai_info['permissions']:
                sub = self._doc.createElement('permission')
                sub.setAttribute('value', permission)
                child.appendChild(sub)
            fragment.appendChild(child)
        return fragment

    def _purgeActions(self):
        self.context._actions = ()

    def _initActions(self, node, mode):
        for child in node.childNodes:
            if child.nodeName != 'action':
                continue
            title = child.getAttribute('title')
            id = child.getAttribute('action_id')
            category = child.getAttribute('category')
            condition = child.getAttribute('condition_expr')
            action = child.getAttribute('url_expr')
            visible = self._convertToBoolean(child.getAttribute('visible'))
            permissions = []
            for sub in child.childNodes:
                if sub.nodeName != 'permission':
                    continue
                permission = sub.getAttribute('value')
                # BBB: for CMF 1.5 profiles
                #      Permission name moved from node text to 'value'.
                if not permission:
                    permission = self._getNodeText(sub)
                permissions.append(permission)
            self.context.addAction(id, title, action, condition,
                                   tuple(permissions), category, visible)

    def _initOldstyleProperties(self, node, mode):
        if not node.hasAttribute('title'):
            return
        # BBB: for CMF 1.5 profiles
        obj = self.context

        title = node.getAttribute('title')
        description = ''
        content_meta_type = node.getAttribute('meta_type')
        content_icon = node.getAttribute('icon')
        immediate_view = node.getAttribute('immediate_view')
        global_allow = self._convertToBoolean(node.getAttribute(
                                                              'global_allow'))
        filter_content_types = self._convertToBoolean(node.getAttribute(
                                                      'filter_content_types'))
        allowed_content_types = []
        allow_discussion = self._convertToBoolean(node.getAttribute(
                                                          'allow_discussion'))
        for child in node.childNodes:
            if child.nodeName == 'description':
                description += self._getNodeText(child)
            elif child.nodeName == 'allowed_content_type':
                allowed_content_types.append(self._getNodeText(child))
        obj._updateProperty('title', title)
        obj._updateProperty('description', description)
        obj._updateProperty('content_meta_type', content_meta_type)
        obj._updateProperty('content_icon', content_icon)
        obj._updateProperty('immediate_view', immediate_view)
        obj._updateProperty('global_allow', global_allow)
        obj._updateProperty('filter_content_types', filter_content_types)
        obj._updateProperty('allowed_content_types', allowed_content_types)
        obj._updateProperty('allow_discussion', allow_discussion)

        if node.getAttribute('kind') == 'Factory-based Type Information':
            product = node.getAttribute('product')
            factory = node.getAttribute('factory')
            obj._updateProperty('product', product)
            obj._updateProperty('factory', factory)
        else:
            constructor_path = node.getAttribute('constructor_path')
            permission = node.getAttribute('permission')
            obj._updateProperty('constructor_path', constructor_path)
            obj._updateProperty('permission', permission)


class TypesToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers,
                          PropertyManagerHelpers):

    """Node im- and exporter for TypesTool.
    """

    __used_for__ = ITypesTool

    _LOGGER_ID = 'typestool'

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractObjects())

        self._logger.info('Types tool exported.')
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        if mode == PURGE:
            self._purgeProperties()
            self._purgeObjects()

        self._initProperties(node, mode)
        self._initObjects(node, mode)
        self._initBBBObjects(node, mode)

        self._logger.info('Types tool imported.')

    def _initBBBObjects(self, node, mode):
        for child in node.childNodes:
            if child.nodeName != 'type':
                continue
            parent = self.context

            obj_id = str(child.getAttribute('id'))
            if obj_id not in parent.objectIds():
                filename = str(child.getAttribute('filename'))
                if not filename:
                    filename = 'types/%s.xml' % obj_id.replace(' ', '_')
                body = self.environ.readDataFile(filename)
                if body is None:
                    break
                root = parseString(body).documentElement
                if root.getAttribute('name') != obj_id:
                    if root.getAttribute('id') != obj_id:
                        break
                meta_type = str(root.getAttribute('kind'))
                if not meta_type:
                    meta_type = str(root.getAttribute('meta_type'))
                for mt_info in Products.meta_types:
                    if mt_info['name'] == meta_type:
                        parent._setObject(obj_id, mt_info['instance'](obj_id))
                        break


def importTypesTool(context):
    """Import types tool and content types from XML files.
    """
    site = context.getSite()
    logger = context.getLogger('typestool')
    tool = getToolByName(site, 'portal_types')

    body = context.readDataFile(_FILENAME)
    if body is None:
        logger.info('Nothing to import.')
        return

    importer = zapi.queryMultiAdapter((tool, context), IBody)
    if importer is None:
        logger.warning('Import adapter misssing.')
        return

    importer.body = body
    importObjects(tool, 'types', context)

def exportTypesTool(context):
    """Export types tool content types as a set of XML files.
    """
    site = context.getSite()
    logger = context.getLogger('typestool')
    tool = getToolByName(site, 'portal_types')
    if tool is None:
        logger.info('Nothing to export.')
        return

    exporter = zapi.queryMultiAdapter((tool, context), IBody)
    if exporter is None:
        logger.warning('Export adapter misssing.')
        return

    context.writeDataFile(_FILENAME, exporter.body, exporter.mime_type)
    exportObjects(tool, 'types', context)
