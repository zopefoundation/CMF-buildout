##parameters=ids=(), **kw
##
from Products.CMFDefault.utils import MessageID as _

if ids:
    return context.setStatus(True)
else:
    return context.setStatus(False, _('Please select one or more members '
                                      'first.'))
