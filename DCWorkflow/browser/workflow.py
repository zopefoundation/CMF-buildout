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
"""DCWorkflowDefinition browser views.

$Id$
"""

from xml.dom.minidom import parseString

from zope.app import zapi

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import IBody

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition


class DCWorkflowDefinitionAddView:

    """Add view for DCWorkflowDefinition.
    """

    title = u'Add DC Workflow Definition'

    description = u'Add a web-configurable workflow.'

    meta_type = DCWorkflowDefinition.meta_type

    def __call__(self, add_input_name='', settings_id='', submit_add=''):
        if submit_add:
            if settings_id:
                profile_id, obj_id = settings_id.split('/')
                if not add_input_name:
                    self.request.set('add_input_name', obj_id)
                obj = DCWorkflowDefinition('temp')
                self._init(obj, profile_id, obj_id)
            else:
                obj = DCWorkflowDefinition('temp')
            self.context.add(obj)
            self.request.response.redirect(self.context.nextURL())
            return ''
        return self.index()

    def getProfileInfos(self):
        profiles = []
        stool = getToolByName(self, 'portal_setup', None)
        if stool:
            for info in stool.listContextInfos():
                obj_ids = []
                context = stool._getImportContext(info['id'])
                dirnames = context.listDirectory('workflows')
                for dirname in dirnames or ():
                    filename = 'workflows/%s/definition.xml' % dirname
                    body = context.readDataFile(filename)
                    if body is None:
                        continue
                    root = parseString(body).documentElement
                    obj_id = root.getAttribute('workflow_id')
                    obj_ids.append(obj_id)
                if not obj_ids:
                    continue
                obj_ids.sort()
                profiles.append({'id': info['id'],
                                 'title': info['title'],
                                 'obj_ids': tuple(obj_ids)})
        return tuple(profiles)

    def _init(self, obj, profile_id, obj_id):
        stool = getToolByName(self, 'portal_setup', None)
        if stool is None:
            return

        context = stool._getImportContext(profile_id)
        file_ids = context.listDirectory('workflows')
        for file_id in file_ids or ():
            filename = 'workflows/%s/definition.xml' % file_id
            body = context.readDataFile(filename)
            if body is None:
                continue

            root = parseString(body).documentElement
            if not root.getAttribute('workflow_id') == obj_id:
                continue

            importer = zapi.queryMultiAdapter((obj, context), IBody)
            if importer is None:
                continue

            importer.body = body
            return
