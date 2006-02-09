##parameters=title, description, **kw
##
from Products.CMFDefault.utils import Message as _

if title!=context.title or description != context.description:
    context.edit(title=title, description=description)
    return context.setStatus(True, _(u'Folder changed.'))
else:
    return context.setStatus(False, _(u'Nothing to change.'))
