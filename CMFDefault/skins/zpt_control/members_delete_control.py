##parameters=ids, **kw
##title=Delete members
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import MessageID as _

mtool = getToolByName(script, 'portal_membership')

mtool.deleteMembers(ids)

if len(ids) == 1:
    return context.setStatus(True, _('Selected member deleted.'))
else:
    return context.setStatus(True, _('Selected members deleted.'))
