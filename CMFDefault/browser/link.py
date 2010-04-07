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
"""Browser views for links.

$Id$
"""

import urlparse

from Products.CMFDefault.exceptions import ResourceLockedError
from Products.CMFDefault.utils import Message as _

from utils import decode
from utils import FormViewBase
from utils import memoize
from utils import ViewBase


class LinkView(ViewBase):

    """View for ILink.
    """

    # interface

    @memoize
    @decode
    def url(self):
        return self.context.getRemoteUrl()


class LinkEditView(FormViewBase):

    """Edit view for IMutableLink.
    """

    _BUTTONS = ({'id': 'change',
                 'title': _(u'Change'),
                 'transform': ('edit_control',),
                 'redirect': ('portal_types', 'object/edit')},
                {'id': 'change_and_view',
                 'title': _(u'Change and View'),
                 'transform': ('edit_control',),
                 'redirect': ('portal_types', 'object/view')})

    # interface

    @memoize
    @decode
    def remote_url(self):
        return self.request.form.get('remote_url', self.context.remote_url)

    # controllers

    def edit_control(self, remote_url, **kw):
        context = self.context
        if remote_url != context.remote_url:
            try:
                context.edit(remote_url=remote_url)
                return True, _(u'Link changed.')
            except ResourceLockedError, errmsg:
                return False, errmsg
        else:
            return False, _(u'Nothing to change.')
