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
"""ActionIconsTool setup handler unit tests.

$Id$
"""
import unittest
#import Testing


from Products.CMFSetup.tests.common import BaseRegistryTests
from Products.CMFSetup.tests.common import DummyExportContext
from Products.CMFSetup.tests.common import DummyImportContext


class _ActionIconsToolSetup(BaseRegistryTests):

    CATEGORY = 'testing'
    ACTION_ID = "test_action"
    TITLE = "Action Title"
    PRIORITY = 60
    ICON_EXPR = 'test_icon'

    _EMPTY_EXPORT = """\
<?xml version="1.0"?>
<action-icons>
</action-icons>
"""

    _WITH_ICON_EXPORT = """\
<?xml version="1.0"?>
<action-icons>
 <action-icon
    category="%s"
    action_id="%s"
    title="%s"
    priority="%d"
    icon_expr="%s"
    />
</action-icons>
""" % (CATEGORY,
       ACTION_ID,
       TITLE,
       PRIORITY,
       ICON_EXPR,
      )

    def _initSite(self, with_icon=False):
        from OFS.Folder import Folder
        from Products.CMFActionIcons.ActionIconsTool import ActionIconsTool

        self.root.site = Folder(id='site')
        site = self.root.site
        tool = ActionIconsTool()
        site._setObject( tool.getId(), tool )

        if with_icon:
            tool.addActionIcon( category=self.CATEGORY
                              , action_id=self.ACTION_ID
                              , title=self.TITLE
                              , priority=self.PRIORITY
                              , icon_expr=self.ICON_EXPR
                              )
        return site

class ActionIconsToolExportConfiguratorTests(_ActionIconsToolSetup):

    def _getTargetClass(self):
        from Products.CMFActionIcons.exportimport \
                import ActionIconsToolExportConfigurator

        return ActionIconsToolExportConfigurator

    def test_generateXML_empty(self):
        site = self._initSite(with_icon=False)
        configurator = self._makeOne(site).__of__(site)

        self._compareDOM(configurator.generateXML(), self._EMPTY_EXPORT)

    def test_generateXML_with_icon(self):
        site = self._initSite(with_icon=True)
        configurator = self._makeOne(site).__of__(site)

        self._compareDOM(configurator.generateXML(), self._WITH_ICON_EXPORT)


class ActionIconsToolImportConfiguratorTests(_ActionIconsToolSetup):

    def _getTargetClass(self):
        from Products.CMFActionIcons.exportimport \
                import ActionIconsToolImportConfigurator

        return ActionIconsToolImportConfigurator

    def test_parseXML_empty(self):
        site = self._initSite(with_icon=False)
        configurator = self._makeOne(site)
        ait_info = configurator.parseXML(self._EMPTY_EXPORT)

        self.assertEqual(len(ait_info['action_icons']), 0)

    def test_parseXML_with_icon(self):
        site = self._initSite(with_icon=False)
        configurator = self._makeOne(site)
        ait_info = configurator.parseXML(self._WITH_ICON_EXPORT)

        self.assertEqual(len(ait_info['action_icons']), 1)

        info = ait_info['action_icons'][0]
        self.assertEqual(info['category'], self.CATEGORY)
        self.assertEqual(info['action_id'], self.ACTION_ID)
        self.assertEqual(info['title'], self.TITLE)
        self.assertEqual(info['priority'], self.PRIORITY)
        self.assertEqual(info['icon_expr'], self.ICON_EXPR)

class Test_exportActionIconsTool(_ActionIconsToolSetup):

    def test_empty(self):
        from Products.CMFActionIcons.exportimport \
            import exportActionIconsTool

        site = self._initSite(with_icon=False)
        context = DummyExportContext(site)
        exportActionIconsTool(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'actionicons.xml')
        self._compareDOM(text, self._EMPTY_EXPORT)
        self.assertEqual(content_type, 'text/xml')

    def test_with_icon(self):
        from Products.CMFActionIcons.exportimport \
            import exportActionIconsTool

        site = self._initSite(with_icon=True)
        context = DummyExportContext(site)
        exportActionIconsTool(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'actionicons.xml')
        self._compareDOM(text, self._WITH_ICON_EXPORT)
        self.assertEqual(content_type, 'text/xml')


class Test_importActionIconsTool(_ActionIconsToolSetup):

    def test_normal(self):
        from Products.CMFActionIcons.exportimport \
            import importActionIconsTool

        site = self._initSite(with_icon=False)
        ait = site.portal_actionicons
        self.assertEqual(len(ait.listActionIcons()), 0)

        context = DummyImportContext(site)
        context._files['actionicons.xml'] = self._WITH_ICON_EXPORT
        importActionIconsTool(context)

        self.assertEqual(len(ait.listActionIcons()), 1)
        action_icon = ait.listActionIcons()[0]

        self.assertEqual(action_icon.getCategory(), self.CATEGORY)
        self.assertEqual(action_icon.getActionId(), self.ACTION_ID)
        self.assertEqual(action_icon.getTitle(), self.TITLE)
        self.assertEqual(action_icon.getPriority(), self.PRIORITY)
        self.assertEqual(action_icon.getExpression(), self.ICON_EXPR)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ActionIconsToolExportConfiguratorTests),
        unittest.makeSuite(ActionIconsToolImportConfiguratorTests),
        unittest.makeSuite(Test_exportActionIconsTool),
        unittest.makeSuite(Test_importActionIconsTool),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
