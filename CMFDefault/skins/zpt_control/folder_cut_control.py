##parameters=ids, **kw
##title=Cut objects from a folder and copy to the clipboard
##
from Products.CMFDefault.exceptions import CopyError
from Products.CMFDefault.utils import MessageID as _

try:
    context.manage_cutObjects(ids, context.REQUEST)
    if len(ids) == 1:
        return context.setStatus(True, _('Item cut.'))
    else:
        return context.setStatus(True, _('Items cut.'))
except CopyError:
    return context.setStatus(False, _('CopyError: Cut failed.'))
