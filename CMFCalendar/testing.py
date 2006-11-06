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
""" Unit test layers.

$Id$
"""

from Products.Five import zcml

from Products.CMFDefault.testing import FunctionalZCMLLayer


class FunctionalZCMLLayer(FunctionalZCMLLayer):

    @classmethod
    def setUp(cls):
        import Products.CMFCalendar

        zcml.load_config('configure.zcml', Products.CMFCalendar)

    @classmethod
    def tearDown(cls):
        pass
