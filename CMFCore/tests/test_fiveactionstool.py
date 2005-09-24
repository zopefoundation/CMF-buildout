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
""" Unit tests for five actions tool.

$Id$
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


def test_fiveactionstool():
    """
    Test the Five actions tool.

    Some basic setup:

      >>> from zope.app.tests.placelesssetup import setUp, tearDown
      >>> setUp()

      >>> import Products.Five
      >>> import Products.CMFCore
      >>> from Products.Five import zcml
      >>> zcml.load_config('meta.zcml', Products.Five)
      >>> zcml.load_config('permissions.zcml', Products.Five)
      >>> zcml.load_config('meta.zcml', Products.CMFCore)
      >>> folder = self.folder

    Let's create a Five actions tool:

      >>> from Products.CMFCore.fiveactionstool import FiveActionsTool
      >>> folder.tool = FiveActionsTool()
      >>> tool = folder.tool # rewrap

    Let's create some simple content object providing ISimpleContent:

      >>> from Products.Five.testing.simplecontent import SimpleContent
      >>> foo = SimpleContent('foo', 'Foo')

    Now we'll load a configuration file specifying some menu and menu
    items for ISimpleContent.

      >>> import Products.CMFCore.tests
      >>> zcml.load_config('fiveactions.zcml', Products.CMFCore.tests)

    Let's look what the tool lists as actions for such an object. Note
    that 'action_content_protected.html' is not present, as it was
    protected by a more restrictive permission:

      >>> actions = tool.listActions(object=foo)
      >>> [(action.category, action.id) for action in actions]
      [('mymenu', 'action_foo_public.html')]

    When looking at an object not implementing ISimpleContent, we see no
    actions:

      >>> tool.listActions(object=folder)
      ()

    The tool itself doesn't have any actions:

      >>> tool.listActions()
      ()

    Cleanup:

      >>> tearDown()
    """

def test_suite():
    from Testing.ZopeTestCase import ZopeDocTestSuite
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()
