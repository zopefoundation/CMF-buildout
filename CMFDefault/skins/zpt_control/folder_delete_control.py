##parameters=ids, **kw
##title=Delete objects from a folder
##
from Products.CMFDefault.utils import MessageID as _

context.manage_delObjects( list(ids) )

if len(ids) == 1:
    return context.setStatus(True, _('Item deleted.'))
else:
    return context.setStatus(True, _('Items deleted.'))
