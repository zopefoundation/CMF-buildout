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
"""Browser views for documents.

$Id$
"""

from Products.CMFDefault.exceptions import EditingConflict
from Products.CMFDefault.exceptions import IllegalHTML
from Products.CMFDefault.exceptions import ResourceLockedError
from Products.CMFDefault.utils import Message as _
from Products.CMFDefault.utils import scrubHTML

from utils import decode
from utils import FormViewBase
from utils import memoize
from utils import ViewBase


class DocumentView(ViewBase):

    """View for IDocument.
    """

    # interface

    @memoize
    @decode
    def text(self):
        return self.context.CookedBody()


class DocumentEditView(FormViewBase):

    """Edit view for IMutableDocument.
    """

    _BUTTONS = ({'id': 'change',
                 'title': _(u'Change'),
                 'transform': ('validateTextFile', 'validateHTML',
                               'edit_control'),
                 'redirect': ('portal_types', 'object/edit')},
                {'id': 'change_and_view',
                 'title': _(u'Change and View'),
                 'transform': ('validateTextFile', 'validateHTML',
                               'edit_control'),
                 'redirect': ('portal_types', 'object/view')})

    #helpers

    @memoize
    def _getHiddenVars(self):
        belt = self.request.form.get('SafetyBelt', self.context.SafetyBelt())
        return {'SafetyBelt': belt}

    # interface

    @memoize
    def text_format(self):
        return self.request.form.get('text_format', self.context.text_format)

    @memoize
    @decode
    def text(self):
        return self.request.form.get('text', self.context.EditableBody())

    # validators

    def validateHTML(self, text, description='', **kw):
        try:
            self.request.form['description'] = scrubHTML(description)
            self.request.form['text'] = scrubHTML(text)
            return True
        except IllegalHTML, errmsg:
            return False, errmsg

    def validateTextFile(self, file='', **kw):
        try:
            upload = file.read()
        except AttributeError:
            return True
        else:
            if upload:
                self.request.form['text'] = upload
                return True
            else:
                return True

    # controllers

    def edit_control(self, text_format, text, SafetyBelt='', **kw):
        context = self.context
        if text_format != context.text_format or \
                text != context.EditableBody():
            try:
                context.edit(text_format, text, safety_belt=SafetyBelt)
                return True, _(u'Document changed.')
            except (ResourceLockedError, EditingConflict), errmsg:
                return False, errmsg
        else:
            return False, _(u'Nothing to change.')
