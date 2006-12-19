##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""CMFDefault browser tests.

$Id$
"""

import unittest
from Testing import ZopeTestCase
from zope.testing import doctest

from Products.CMFDefault.testing import FunctionalLayer


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite('folder.txt',
                                    optionflags=doctest.NORMALIZE_WHITESPACE))
    s = ZopeTestCase.FunctionalDocFileSuite('metadata.txt')
    s.layer = FunctionalLayer
    suite.addTest(s)
    return suite

if __name__ == '__main__':
    from Products.CMFCore.testing import run
    run(test_suite())
