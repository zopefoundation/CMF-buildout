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
"""Workflow tool xml adapters and setup handlers.

$Id$
"""

import Products
from zope.app import zapi

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import PURGE
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase

from Products.CMFCore.interfaces import IWorkflowTool
from Products.CMFCore.utils import getToolByName

_FILENAME = 'workflows.xml'


class WorkflowToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers,
                             PropertyManagerHelpers):

    """XML im- and exporter for WorkflowTool.
    """

    __used_for__ = IWorkflowTool

    _LOGGER_ID = 'workflow'

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractObjects())
        node.appendChild(self._extractChains())

        self._logger.info('Workflow tool exported.')
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        if mode == PURGE:
            self._purgeProperties()
            self._purgeObjects()
            self._purgeChains()

        self._initProperties(node, mode)
        self._initObjects(node, mode)
        self._initBBBObjects(node, mode)
        self._initChains(node, mode)

        self._logger.info('Workflow tool imported.')

    def _initBBBObjects(self, node, mode):
        for child in node.childNodes:
            if child.nodeName != 'workflow':
                continue
            parent = self.context

            obj_id = str(child.getAttribute('workflow_id'))
            if obj_id not in parent.objectIds():
                meta_type = str(child.getAttribute('meta_type'))
                for mt_info in Products.meta_types:
                    if mt_info['name'] == meta_type:
                        parent._setObject(obj_id, mt_info['instance'](obj_id))
                        break

    def _extractChains(self):
        fragment = self._doc.createDocumentFragment()
        node = self._doc.createElement('bindings')
        child = self._doc.createElement('default')
        chain = self.context._default_chain
        for workflow_id in chain:
            sub = self._doc.createElement('bound-workflow')
            sub.setAttribute('workflow_id', workflow_id)
            child.appendChild(sub)
        node.appendChild(child)
        cbt = self.context._chains_by_type
        if cbt:
            overrides = cbt.items()
            overrides.sort()
            for type_id, chain in overrides:
                child = self._doc.createElement('type')
                child.setAttribute('type_id', type_id)
                for workflow_id in chain:
                    sub = self._doc.createElement('bound-workflow')
                    sub.setAttribute('workflow_id', workflow_id)
                    child.appendChild(sub)
                node.appendChild(child)
        fragment.appendChild(node)
        return fragment

    def _purgeChains(self):
        self.context.setDefaultChain('')
        if self.context._chains_by_type is not None:
            self.context._chains_by_type.clear()

    def _initChains(self, node, mode):
        for child in node.childNodes:
            if child.nodeName != 'bindings':
                continue
            for sub in child.childNodes:
                if sub.nodeName == 'default':
                    self.context.setDefaultChain(self._getChain(sub))
                if sub.nodeName == 'type':
                    type_id = str(sub.getAttribute('type_id'))
                    self.context.setChainForPortalTypes((type_id,),
                                            self._getChain(sub), verify=False)

    def _getChain(self, node):
        workflow_ids = []
        for child in node.childNodes:
            if child.nodeName != 'bound-workflow':
                continue
            workflow_ids.append(str(child.getAttribute('workflow_id')))
        return ','.join(workflow_ids)


def importWorkflowTool(context):
    """Import workflow tool and contained workflow definitions from XML files.
    """
    site = context.getSite()
    logger = context.getLogger('workflow')
    tool = getToolByName(site, 'portal_workflow')

    body = context.readDataFile(_FILENAME)
    if body is None:
        logger.info('Nothing to import.')
        return

    importer = zapi.queryMultiAdapter((tool, context), IBody)
    if importer is None:
        logger.warning('Import adapter misssing.')
        return

    importer.body = body
    importObjects(tool, 'workflows', context)

def exportWorkflowTool(context):
    """Export workflow tool and contained workflow definitions as XML files.
    """
    site = context.getSite()
    logger = context.getLogger('workflow')
    tool = getToolByName(site, 'portal_workflow')
    if tool is None:
        logger.info('Nothing to export.')
        return

    exporter = zapi.queryMultiAdapter((tool, context), IBody)
    if exporter is None:
        logger.warning('Export adapter misssing.')
        return

    context.writeDataFile(_FILENAME, exporter.body, exporter.mime_type)
    exportObjects(tool, 'workflows', context)
