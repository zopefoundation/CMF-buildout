##parameters=id='', **kw
##
from Products.CMFDefault.utils import MessageID as _

if id:
    if context.checkIdAvailable(id):
        return context.setStatus(True)
    else:
        return context.setStatus(False, _('Please choose another ID.'))
else:
    return context.setStatus(False, _('Please enter an ID.'))
