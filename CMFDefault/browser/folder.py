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
"""Browser views for folders.

$Id$
"""

from DocumentTemplate import sequence
from ZTUtils import LazyFilter
from ZTUtils import make_query

from Products.CMFDefault.exceptions import CopyError
from Products.CMFDefault.exceptions import zExceptions_Unauthorized
from Products.CMFDefault.permissions import AddPortalContent
from Products.CMFDefault.permissions import DeleteObjects
from Products.CMFDefault.permissions import ListFolderContents
from Products.CMFDefault.permissions import ManageProperties
from Products.CMFDefault.permissions import ViewManagementScreens
from Products.CMFDefault.utils import Message as _

from utils import BatchViewBase
from utils import decode
from utils import FormViewBase
from utils import memoize


class FolderView(BatchViewBase):

    """View for IFolderish.
    """

    # helpers

    @memoize
    def _getItems(self):
        (key, reverse) = self.context.getDefaultSorting()
        items = self.context.contentValues()
        items = sequence.sort(items,
                              ((key, 'cmp', reverse and 'desc' or 'asc'),))
        return LazyFilter(items, skip='View')

    # interface

    @memoize
    def has_local(self):
        return 'local_pt' in self.context.objectIds()


class FolderContentsView(BatchViewBase, FormViewBase):

    """Contents view for IFolderish.
    """

    _BUTTONS = ({'id': 'items_new',
                 'title': _(u'New...'),
                 'permissions': (ViewManagementScreens, AddPortalContent),
                 'conditions': ('checkAllowedContentTypes',),
                 'redirect': ('portal_types', 'object/new')},
                {'id': 'items_rename',
                 'title': _(u'Rename...'),
                 'permissions': (ViewManagementScreens, AddPortalContent),
                 'conditions': ('checkItems', 'checkAllowedContentTypes'),
                 'transform': ('validateItemIds',),
                 'redirect': ('portal_types', 'object/rename_items',
                              'b_start, ids, key, reverse')},
                {'id': 'items_cut',
                 'title': _(u'Cut'),
                 'permissions': (ViewManagementScreens,),
                 'conditions': ('checkItems',),
                 'transform': ('validateItemIds', 'cut_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')},
                {'id': 'items_copy',
                 'title': _(u'Copy'),
                 'permissions': (ViewManagementScreens,),
                 'conditions': ('checkItems',),
                 'transform': ('validateItemIds', 'copy_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')},
                {'id': 'items_paste',
                 'title': _(u'Paste'),
                 'permissions': (ViewManagementScreens, AddPortalContent),
                 'conditions': ('checkClipboardData',),
                 'transform': ('validateClipboardData', 'paste_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')},
                {'id': 'items_delete',
                 'title': _(u'Delete'),
                 'permissions': (ViewManagementScreens, DeleteObjects),
                 'conditions': ('checkItems',),
                 'transform': ('validateItemIds', 'delete_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')},
                {'id': 'items_sort',
                 'permissions': (ManageProperties,),
                 'transform': ('sort_control',),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start')},
                {'id': 'items_up',
                 'permissions': (ManageProperties,),
                 'transform': ('validateItemIds', 'up_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')},
                {'id': 'items_down',
                 'permissions': (ManageProperties,),
                 'transform': ('validateItemIds', 'down_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')},
                {'id': 'items_top',
                 'permissions': (ManageProperties,),
                 'transform': ('validateItemIds', 'top_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')},
                {'id': 'items_bottom',
                 'permissions': (ManageProperties,),
                 'transform': ('validateItemIds', 'bottom_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')})

    # helpers

    @memoize
    def _getSorting(self):
        key = self.request.form.get('key', None)
        if key:
            return (key, self.request.form.get('reverse', 0))
        else:
            return self.context.getDefaultSorting()

    @memoize
    def _isDefaultSorting(self):
        return self._getSorting() == self.context.getDefaultSorting()

    @memoize
    def _getHiddenVars(self):
        b_start = self._getBatchStart()
        is_default = self._isDefaultSorting()
        (key, reverse) = is_default and ('', 0) or self._getSorting()
        return {'b_start': b_start, 'key': key, 'reverse': reverse}

    @memoize
    def _getItems(self):
        (key, reverse) = self._getSorting()
        self.context.filterCookie()
        folderfilter = self.request.get('folderfilter', '')
        filter = self.context.decodeFolderFilter(folderfilter)
        items = self.context.listFolderContents(contentFilter=filter)
        return sequence.sort(items,
                             ((key, 'cmp', reverse and 'desc' or 'asc'),))

    # interface

    @memoize
    @decode
    def up_info(self):
        mtool = self._getTool('portal_membership')
        allowed = mtool.checkPermission(ListFolderContents, self.context,
                                        'aq_parent')
        if allowed:
            up_obj = self.context.aq_inner.aq_parent
            if hasattr(up_obj, 'portal_url'):
                up_url = up_obj.getActionInfo('object/folderContents')['url']
                return {'icon': '%s/UpFolder_icon.gif' % self._getPortalURL(),
                        'id': up_obj.getId(),
                        'url': up_url}
            else:
                return {'icon': '',
                        'id': 'Root',
                        'url': ''}
        else:
            return {}

    @memoize
    def listColumnInfos(self):
        (key, reverse) = self._getSorting()
        columns = ( {'key': 'Type',
                     'title': _(u'Type'),
                     'width': '20',
                     'colspan': '2'}
                  , {'key': 'getId',
                     'title': _(u'Name'),
                     'width': '360',
                     'colspan': None}
                  , {'key': 'modified',
                     'title': _(u'Last Modified'),
                     'width': '180',
                     'colspan': None}
                  , {'key': 'position',
                     'title': _(u'Position'),
                     'width': '80',
                     'colspan': None }
                  )
        for column in columns:
            if key == column['key'] and not reverse and key != 'position':
                query = make_query(key=column['key'], reverse=1)
            else:
                query = make_query(key=column['key'])
            column['url'] = '%s?%s' % (self._getViewURL(), query)
        return tuple(columns)

    @memoize
    @decode
    def listItemInfos(self):
        b_start = self._getBatchStart()
        (key, reverse) = self._getSorting()
        batch_obj = self._getBatchObj()
        items_manage_allowed = self._checkPermission(ViewManagementScreens)
        portal_url = self._getPortalURL()

        items = []
        i = 1
        for item in batch_obj:
            item_icon = item.getIcon(1)
            item_id = item.getId()
            item_position = (key == 'position') and str(b_start + i) or '...'
            i += 1
            item_url = item.getActionInfo(('object/folderContents',
                                           'object/view'))['url']
            items.append({'checkbox': items_manage_allowed and ('cb_%s' %
                                                               item_id) or '',
                          'icon': item_icon and ('%s/%s' %
                                               (portal_url, item_icon)) or '',
                          'id': item_id,
                          'modified': item.ModificationDate(),
                          'position': item_position,
                          'title': item.Title(),
                          'type': item.Type() or None,
                          'url': item_url})
        return tuple(items)

    @memoize
    def listDeltas(self):
        length = self._getBatchObj().sequence_length
        deltas = range(1, min(5, length)) + range(5, length, 5)
        return tuple(deltas)

    @memoize
    def is_orderable(self):
        length = len(self._getBatchObj())
        items_move_allowed = self._checkPermission(ManageProperties)
        (key, reverse) = self._getSorting()
        return items_move_allowed and (key == 'position') and length > 1

    @memoize
    def is_sortable(self):
        items_move_allowed = self._checkPermission(ManageProperties)
        return items_move_allowed and not self._isDefaultSorting()

    # checkers

    def checkAllowedContentTypes(self):
        return bool(self.context.allowedContentTypes())

    def checkClipboardData(self):
        return bool(self.context.cb_dataValid())

    def checkItems(self):
        return bool(self._getItems())

    # validators

    def validateItemIds(self, ids=(), **kw):
        if ids:
            return True
        else:
            return False, _(u'Please select one or more items first.')

    def validateClipboardData(self, **kw):
        if self.context.cb_dataValid():
            return True
        else:
            return False, _(u'Please copy or cut one or more items to paste '
                            u'first.')

    # controllers

    def cut_control(self, ids, **kw):
        """Cut objects from a folder and copy to the clipboard.
        """
        try:
            self.context.manage_cutObjects(ids, self.request)
            if len(ids) == 1:
                return True, _(u'Item cut.')
            else:
                return True, _(u'Items cut.')
        except CopyError:
            return False, _(u'CopyError: Cut failed.')
        except zExceptions_Unauthorized:
            return False, _(u'Unauthorized: Cut failed.')

    def copy_control(self, ids, **kw):
        """Copy objects from a folder to the clipboard.
        """
        try:
            self.context.manage_copyObjects(ids, self.request)
            if len(ids) == 1:
                return True, _(u'Item copied.')
            else:
                return True, _(u'Items copied.')
        except CopyError:
            return False, _(u'CopyError: Copy failed.')

    def paste_control(self, **kw):
        """Paste objects to a folder from the clipboard.
        """
        try:
            result = self.context.manage_pasteObjects(self.request['__cp'])
            if len(result) == 1:
                return True, _(u'Item pasted.')
            else:
                return True, _(u'Items pasted.')
        except CopyError:
            return False, _(u'CopyError: Paste failed.')
        except zExceptions_Unauthorized:
            return False, _(u'Unauthorized: Paste failed.')

    def delete_control(self, ids, **kw):
        """Delete objects from a folder.
        """
        self.context.manage_delObjects(list(ids))
        if len(ids) == 1:
            return True, _(u'Item deleted.')
        else:
            return True, _(u'Items deleted.')

    def sort_control(self, key='position', reverse=0, **kw):
        """Sort objects in a folder.
        """
        self.context.setDefaultSorting(key, reverse)
        return True

    def up_control(self, ids, delta, **kw):
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
        try:
            attempt = self.context.moveObjectsUp(ids, delta,
                                                 subset_ids=subset_ids)
            if attempt == 1:
                return True, _(u'Item moved up.')
            elif attempt > 1:
                return True, _(u'Items moved up.')
            else:
                return False, _(u'Nothing to change.')
        except ValueError:
            return False, _(u'ValueError: Move failed.')

    def down_control(self, ids, delta, **kw):
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
        try:
            attempt = self.context.moveObjectsDown(ids, delta,
                                                   subset_ids=subset_ids)
            if attempt == 1:
                return True, _(u'Item moved down.')
            elif attempt > 1:
                return True, _(u'Items moved down.')
            else:
                return False, _(u'Nothing to change.')
        except ValueError:
            return False, _(u'ValueError: Move failed.')

    def top_control(self, ids, **kw):
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
        try:
            attempt = self.context.moveObjectsToTop(ids,
                                                    subset_ids=subset_ids)
            if attempt == 1:
                return True, _(u'Item moved to top.')
            elif attempt > 1:
                return True, _(u'Items moved to top.')
            else:
                return False, _(u'Nothing to change.')
        except ValueError:
            return False, _(u'ValueError: Move failed.')

    def bottom_control(self, ids, **kw):
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
        try:
            attempt = self.context.moveObjectsToBottom(ids,
                                                       subset_ids=subset_ids)
            if attempt == 1:
                return True, _(u'Item moved to bottom.')
            elif attempt > 1:
                return True, _(u'Items moved to bottom.')
            else:
                return False, _(u'Nothing to change.')
        except ValueError:
            return False, _(u'ValueError: Move failed.')
