##parameters=text_format, text, description='', **kw
##
from Products.CMFDefault.exceptions import ResourceLockedError
from Products.CMFDefault.utils import MessageID as _

if description != context.description or \
        text_format != context.text_format or text != context.text:
    try:
        context.edit(text=text, description=description,
                     text_format=text_format)
        return context.setStatus(True, _('News Item changed.'))
    except ResourceLockedError, errmsg:
        return context.setStatus(False, errmsg)
else:
    return context.setStatus(False, _('Nothing to change.'))
