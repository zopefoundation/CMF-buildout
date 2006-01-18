##parameters=title, description, **kw
##
from Products.CMFDefault.utils import Message as _

if title!=context.title or description != context.description:
    context.edit(title=title, description=description)
    return context.setStatus(True, _('Folder changed.'))
else:
    return context.setStatus(False, _('Nothing to change.'))
