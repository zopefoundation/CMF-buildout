##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser views for news items.

$Id$
"""

from Products.CMFDefault.exceptions import ResourceLockedError
from Products.CMFDefault.utils import Message as _

from document import DocumentEditView
from utils import decode
from utils import memoize


class NewsItemEditView(DocumentEditView):

    """Edit view for INewsItem.
    """

    # interface

    @memoize
    @decode
    def description(self):
        return self.request.form.get('description',
                                     self.context.Description())

    # controllers

    def edit_control(self, text_format, text, description='', **kw):
        context = self.context
        if description != context.Description() or \
                text_format != context.text_format or \
                text != context.EditableBody():
            try:
                context.edit(text=text, description=description,
                             text_format=text_format)
                return True, _(u'News Item changed.')
            except ResourceLockedError, errmsg:
                return False, errmsg
        else:
            return False, _(u'Nothing to change.')
