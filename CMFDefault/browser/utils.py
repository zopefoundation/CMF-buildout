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
"""Browser view utilities.

$Id$
"""

from AccessControl.SecurityInfo import ClassSecurityInfo
from DateTime.DateTime import DateTime
from Globals import InitializeClass
from Products.Five import BrowserView
from Products.PythonScripts.standard import thousands_commas
from ZTUtils import Batch
from ZTUtils import make_query

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.permissions import View
from Products.CMFDefault.utils import html_marshal
from Products.CMFDefault.utils import Message as _
from Products.CMFDefault.utils import translate
from Products.CMFDefault.utils import toUnicode


def decode(meth):
    def decoded_meth(self, *args, **kw):
        return toUnicode(meth(self, *args, **kw), self._getDefaultCharset())
    return decoded_meth

def memoize(meth):
    def memoized_meth(self, *args):
        if not hasattr(self, '__memo__'):
            self.__memo__ = {}
        sig = (meth, args)
        if sig not in self.__memo__:
            self.__memo__[sig] = meth(self, *args)
        return self.__memo__[sig]
    return memoized_meth


class MacroView(BrowserView):

    """Allows to use macros from non-view templates.
    """
    
    # The following allows to traverse the view/class and reach
    # macros defined in page templates, e.g. in a use-macro.
    security = ClassSecurityInfo()

    def _macros(self):
        return self.index.macros

    security.declareProtected(View, 'macros')
    macros = property(_macros, None, None)

InitializeClass(MacroView)


class ViewBase(BrowserView):

    # helpers

    @memoize
    def _getTool(self, name):
        return getToolByName(self.context, name)

    @memoize
    def _checkPermission(self, permission):
        mtool = self._getTool('portal_membership')
        return mtool.checkPermission(permission, self.context)

    @memoize
    def _getPortalURL(self):
        utool = self._getTool('portal_url')
        return utool()

    @memoize
    def _getViewURL(self):
        return self.request['ACTUAL_URL']

    @memoize
    def _getDefaultCharset(self):
        ptool = self._getTool('portal_properties')
        return ptool.getProperty('default_charset', None)

    # interface

    @memoize
    @decode
    def title(self):
        return self.context.Title()

    @memoize
    @decode
    def description(self):
        return self.context.Description()


class FormViewBase(ViewBase):

    # helpers

    def _setRedirect(self, provider_id, action_path, keys=''):
        provider = self._getTool(provider_id)
        try:
            target = provider.getActionInfo(action_path, self.context)['url']
        except ValueError:
            target = self._getPortalURL()

        kw = {}
        message = self.request.other.get('portal_status_message', '')
        if message:
            if isinstance(message, unicode):
                message = message.encode(self._getDefaultCharset())
            kw['portal_status_message'] = message
        for k in keys.split(','):
            k = k.strip()
            v = self.request.form.get(k, None)
            if v:
                kw[k] = v

        query = kw and ( '?%s' % make_query(kw) ) or ''
        self.request.RESPONSE.redirect( '%s%s' % (target, query) )

        return True

    # interface

    def __call__(self, **kw):
        form = self.request.form
        for button in self._BUTTONS:
            if button['id'] in form:
                for permission in button.get('permissions', ()):
                    if not self._checkPermission(permission):
                        break
                else:
                    for transform in button.get('transform', ()):
                        status = getattr(self, transform)(**form)
                        if isinstance(status, bool):
                            status = (status,)
                        if len(status) > 1:
                            message = translate(status[1], self.context)
                            self.request.other['portal_status_message'] = message
                        if not status[0]:
                            return self.index()
                    if self._setRedirect(*button['redirect']):
                        return
        return self.index()

    @memoize
    def form_action(self):
        return self._getViewURL()

    @memoize
    def listButtonInfos(self):
        form = self.request.form
        buttons = []
        for button in self._BUTTONS:
            if button.get('title', None):
                for permission in button.get('permissions', ()):
                    if not self._checkPermission(permission):
                        break
                else:
                    for condition in button.get('conditions', ()):
                        if not getattr(self, condition)():
                            break
                    else:
                        buttons.append({'name': button['id'],
                                        'value': button['title']})
        return tuple(buttons)

    @memoize
    @decode
    def listHiddenVarInfos(self):
        kw = self._getHiddenVars()
        vars = [ {'name': name, 'value': value}
                 for name, value in html_marshal(**kw) ]
        return tuple(vars)


class BatchViewBase(ViewBase):

    # helpers

    _BATCH_SIZE = 25

    @memoize
    def _getBatchStart(self):
        return self.request.form.get('b_start', 0)

    @memoize
    def _getBatchObj(self):
        b_start = self._getBatchStart()
        items = self._getItems()
        return Batch(items, self._BATCH_SIZE, b_start, orphan=0)

    @memoize
    def _getHiddenVars(self):
        return {}

    @memoize
    def _getNavigationVars(self):
        return self._getHiddenVars()

    @memoize
    def _getNavigationURL(self, b_start):
        target = self._getViewURL()
        kw = self._getNavigationVars().copy()

        kw['b_start'] = b_start
        for k, v in kw.items():
            if not v or k == 'portal_status_message':
                del kw[k]

        query = kw and ('?%s' % make_query(kw)) or ''
        return u'%s%s' % (target, query)

    # interface

    @memoize
    @decode
    def listItemInfos(self):
        batch_obj = self._getBatchObj()
        portal_url = self._getPortalURL()

        items = []
        for item in batch_obj:
            item_description = item.Description()
            item_icon = item.getIcon(1)
            item_title = item.Title()
            item_type = remote_type = item.Type()
            if item_type == 'Favorite' and not item_icon == 'p_/broken':
                item = item.getObject()
                item_description = item_description or item.Description()
                item_title = item_title or item.Title()
                remote_type = item.Type()
            is_file = remote_type in ('File', 'Image')
            is_link = remote_type == 'Link'
            items.append({'description': item_description,
                          'format': is_file and item.Format() or '',
                          'icon': item_icon and ('%s/%s' %
                                               (portal_url, item_icon)) or '',
                          'size': is_file and ('%0.0f kb' %
                                            (item.get_size() / 1024.0)) or '',
                          'title': item_title,
                          'type': item_type,
                          'url': is_link and item.getRemoteUrl() or
                                 item.absolute_url()})
        return tuple(items)

    @memoize
    def navigation_previous(self):
        batch_obj = self._getBatchObj().previous
        if batch_obj is None:
            return None

        length = len(batch_obj)
        url = self._getNavigationURL(batch_obj.first)
        if length == 1:
            title = _(u'Previous item')
        else:
            title = _(u'Previous ${count} items', mapping={'count': length})
        return {'title': title, 'url': url}

    @memoize
    def navigation_next(self):
        batch_obj = self._getBatchObj().next
        if batch_obj is None:
            return None

        length = len(batch_obj)
        url = self._getNavigationURL(batch_obj.first)
        if length == 1:
            title = _(u'Next item')
        else:
            title = _(u'Next ${count} items', mapping={'count': length})
        return {'title': title, 'url': url}

    @memoize
    def summary_length(self):
        length = self._getBatchObj().sequence_length
        return length and thousands_commas(length) or ''

    @memoize
    def summary_type(self):
        length = self._getBatchObj().sequence_length
        return (length == 1) and _(u'item') or _(u'items')

    @memoize
    @decode
    def summary_match(self):
        return self.request.form.get('SearchableText')
