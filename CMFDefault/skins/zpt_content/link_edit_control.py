##parameters=remote_url, **kw
##
from Products.CMFDefault.exceptions import ResourceLockedError
from Products.CMFDefault.utils import MessageID as _

if remote_url != context.remote_url:
    try:
        context.edit(remote_url=remote_url)
        return context.setStatus(True, _('Link changed.'))
    except ResourceLockedError, errmsg:
        return context.setStatus(False, errmsg)
else:
    return context.setStatus(False, _('Nothing to change.'))
