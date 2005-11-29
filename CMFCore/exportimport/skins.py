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
"""Skins tool xml adapters and setup handlers.

$Id$
"""

from zope.app import zapi

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import PURGE
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import NodeAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase

from Products.CMFCore.DirectoryView import createDirectoryView
from Products.CMFCore.interfaces import IDirectoryView
from Products.CMFCore.interfaces import ISkinsTool
from Products.CMFCore.utils import getToolByName

_FILENAME = 'skins.xml'


class DirectoryViewNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for DirectoryView.
    """

    __used_for__ = IDirectoryView

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._getObjectNode('object')
        node.setAttribute('directory', self.context.getDirPath())
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        self.context.manage_properties(str(node.getAttribute('directory')))


class SkinsToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers):

    """XML im- and exporter for SkinsTool.
    """

    __used_for__ = ISkinsTool

    _LOGGER_ID = 'skins'

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._getObjectNode('object')
        node.setAttribute('default_skin', self.context.default_skin)
        node.setAttribute('request_varname', self.context.request_varname)
        node.setAttribute('allow_any', str(bool(self.context.allow_any)))
        node.setAttribute('cookie_persistence',
                          str(bool(self.context.cookie_persistence)))
        node.appendChild(self._extractObjects())
        node.appendChild(self._extractSkinPaths())

        self._logger.info('Skins tool exported.')
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        obj = self.context

        if mode == PURGE:
            obj.default_skin = ''
            obj.request_varname = 'portal_skin'
            obj.allow_any = 0
            obj.cookie_persistence = 0
            self._purgeObjects()
            self._purgeSkinPaths()

        if node.hasAttribute('default_skin'):
            obj.default_skin = str(node.getAttribute('default_skin'))
        if node.hasAttribute('request_varname'):
            obj.request_varname = str(node.getAttribute('request_varname'))
        if node.hasAttribute('allow_any'):
            allow_any = node.getAttribute('allow_any')
            obj.allow_any = int(self._convertToBoolean(allow_any))
        if node.hasAttribute('cookie_persistence'):
            persistence = node.getAttribute('cookie_persistence')
            obj.cookie_persistence = int(self._convertToBoolean(persistence))
        self._initObjects(node, mode)
        self._initBBBObjects(node, mode)
        self._initSkinPaths(node, mode)

        self._logger.info('Skins tool imported.')

    def _initBBBObjects(self, node, mode):
        for child in node.childNodes:
            if child.nodeName != 'skin-directory':
                continue
            parent = self.context

            obj_id = str(child.getAttribute('id'))
            obj_dir = str(child.getAttribute('directory'))
            if obj_id not in parent.objectIds():
                createDirectoryView(self.context, obj_dir, obj_id)

    def _extractSkinPaths(self):
        fragment = self._doc.createDocumentFragment()
        for k, v in self.context.getSkinPaths():
            node = self._doc.createElement('skin-path')
            node.setAttribute('name', k)
            for layer in [ l.strip() for l in v.split(',') if l.strip() ]:
                child = self._doc.createElement('layer')
                child.setAttribute('name', layer)
                node.appendChild(child)
            fragment.appendChild(node)
        return fragment

    def _purgeSkinPaths(self):
        self.context._getSelections().clear()

    def _initSkinPaths(self, node, mode):
        for child in node.childNodes:
            if child.nodeName != 'skin-path':
                continue
            path_id = str(child.getAttribute('name'))
            if not path_id:
                #BBB
                path_id = str(child.getAttribute('id'))
            if path_id == '*':
                for path_id, path in self.context._getSelections().items():
                    path = self._updatePath(path, child)
                    self.context.addSkinSelection(path_id, path)
            else:
                if path_id in self.context._getSelections():
                    path = self.context._getSelections()[path_id]
                else:
                    path = ''
                path = self._updatePath(path, child)
                self.context.addSkinSelection(path_id, path)
        #
        # Purge and rebuild the skin path, now that we have added our stuff.
        # Don't bother if no REQUEST is present, e.g. when running unit tests
        #
        site = self.environ.getSite()
        request = getattr(site, 'REQUEST', None)
        if request is not None:
            site.clearCurrentSkin()
            site.setupCurrentSkin(request)


    def _updatePath(self, path, node):
        path = [ name.strip() for name in path.split(',') if name.strip() ]

        for child in node.childNodes:
            if child.nodeName != 'layer':
                continue
            layer_name = child.getAttribute('name')
            if layer_name in path:
                path.remove(layer_name)

            if child.hasAttribute('insert-before'):
                insert_before = child.getAttribute('insert-before')
                if insert_before == '*':
                    path.insert(0, layer_name)
                    continue
                else:
                    try:
                        index = path.index(insert_before)
                        path.insert(index, layer_name)
                        continue
                    except ValueError:
                        pass
            elif child.hasAttribute('insert-after'):
                insert_after = child.getAttribute('insert-after')
                if insert_after == '*':
                    pass
                else:
                    try:
                        index = path.index(insert_after)
                        path.insert(index+1, layer_name)
                        continue
                    except ValueError:
                        pass

            if not child.hasAttribute('remove'):
                path.append(layer_name)

        return str( ','.join(path) )


def importSkinsTool(context):
    """Import skins tool FSDirViews and skin paths from an XML file.
    """
    site = context.getSite()
    logger = context.getLogger('skins')
    tool = getToolByName(site, 'portal_skins')

    body = context.readDataFile(_FILENAME)
    if body is None:
        logger.info('Nothing to import.')
        return

    importer = zapi.queryMultiAdapter((tool, context), IBody)
    if importer is None:
        logger.warning('Import adapter misssing.')
        return

    importer.body = body
    importObjects(tool, 'skins', context)

def exportSkinsTool(context):
    """Export skins tool FSDVs and skin paths as an XML file.
    """
    site = context.getSite()
    logger = context.getLogger('skins')
    tool = getToolByName(site, 'portal_skins', None)
    if tool is None:
        logger.info('Nothing to export.')
        return

    exporter = zapi.queryMultiAdapter((tool, context), IBody)
    if exporter is None:
        logger.warning('Export adapter misssing.')
        return

    context.writeDataFile(_FILENAME, exporter.body, exporter.mime_type)
    exportObjects(tool, 'skins', context)
