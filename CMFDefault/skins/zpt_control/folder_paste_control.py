##parameters=**kw
##title=Paste objects to a folder from the clipboard
##
from Products.CMFDefault.exceptions import CopyError
from Products.CMFDefault.exceptions import zExceptions_Unauthorized
from Products.CMFDefault.utils import MessageID as _

if context.cb_dataValid:
    try:
        result = context.manage_pasteObjects(context.REQUEST['__cp'])
        if len(ids) == 1:
            return context.setStatus(True, _('Item pasted.'))
        else:
            return context.setStatus(True, _('Items pasted.'))
    except CopyError:
        return context.setStatus(False, _('CopyError: Paste failed.'))
    except zExceptions_Unauthorized:
        return context.setStatus(False, _('Unauthorized: Paste failed.'))
else:
    return context.setStatus(False, _('Please copy or cut one or more items '
                                      'to paste first.'))
