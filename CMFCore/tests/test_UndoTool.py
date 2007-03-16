##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for UndoTool module.

$Id$
"""

import unittest
import Testing

from zope.interface.verify import verifyClass


class UndoToolTests(unittest.TestCase):

    def test_interfaces(self):
        from Products.CMFCore.interfaces import IActionProvider
        from Products.CMFCore.interfaces import IUndoTool
        from Products.CMFCore.UndoTool import UndoTool

        verifyClass(IActionProvider, UndoTool)
        verifyClass(IUndoTool, UndoTool)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(UndoToolTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
