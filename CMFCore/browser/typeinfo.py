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
"""TypeInformation browser views.

$Id$
"""

from xml.dom.minidom import parseString

from zope.app import zapi

from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.TypesTool import ScriptableTypeInformation
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.browser.utils import AddWithPresettingsViewBase
from Products.GenericSetup.interfaces import IBody


class FactoryTypeInformationAddView(AddWithPresettingsViewBase):

    """Add view for FactoryTypeInformation.
    """

    klass = FactoryTypeInformation

    description = u'A type information object defines a portal type.'

    def getProfileInfos(self):
        profiles = []
        stool = getToolByName(self, 'portal_setup', None)
        if stool:
            for info in stool.listContextInfos():
                obj_ids = []
                context = stool._getImportContext(info['id'])
                file_ids = context.listDirectory('types')
                for file_id in file_ids or ():
                    filename = 'types/%s' % file_id
                    body = context.readDataFile(filename)
                    if body is None:
                        continue
                    root = parseString(body).documentElement
                    obj_id = root.getAttribute('name')
                    if not obj_id:
                        obj_id = root.getAttribute('id')
                    if root.getAttribute('meta_type') != self.klass.meta_type:
                        continue
                    obj_ids.append(obj_id)
                if not obj_ids:
                    continue
                obj_ids.sort()
                profiles.append({'id': info['id'],
                                 'title': info['title'],
                                 'obj_ids': tuple(obj_ids)})
        return tuple(profiles)

    def _initSettings(self, obj, profile_id, obj_id):
        stool = getToolByName(self, 'portal_setup', None)
        if stool is None:
            return

        context = stool._getImportContext(profile_id)
        file_ids = context.listDirectory('types')
        for file_id in file_ids or ():
            filename = 'types/%s' % file_id
            body = context.readDataFile(filename)
            if body is None:
                continue

            root = parseString(body).documentElement
            new_id = root.getAttribute('name')
            if not new_id:
                new_id = root.getAttribute('id')
            if new_id != obj_id:
                continue

            if root.getAttribute('meta_type') != self.klass.meta_type:
                continue

            importer = zapi.queryMultiAdapter((obj, context), IBody)
            if importer is None:
                continue

            importer.body = body
            return


class ScriptableTypeInformationAddView(FactoryTypeInformationAddView):

    """Add view for ScriptableTypeInformation.
    """

    klass = ScriptableTypeInformation