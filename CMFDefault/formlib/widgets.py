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
"""Custom form widgets.

$Id$
"""

from zope.app.form.browser import TextWidget
from zope.app.form.interfaces import ConversionError
from zope.app.form.interfaces import IInputWidget
from zope.component import adapts
from zope.interface import implementsOnly
from zope.publisher.interfaces.browser import IBrowserRequest

from Products.CMFDefault.formlib.schema import IEmailLine
from Products.CMFDefault.utils import Message as _


class EmailInputWidget(TextWidget):

    implementsOnly(IInputWidget)
    adapts(IEmailLine, IBrowserRequest)

    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value

        try:
            return str(input.strip())
        except (AttributeError, UnicodeEncodeError), err:
            raise ConversionError(_(u'Invalid email address.'), err)
