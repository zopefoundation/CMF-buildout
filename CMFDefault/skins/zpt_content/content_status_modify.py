##parameters=workflow_action, comment=''
##title=Modify the status of a content object
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import Message as _

wtool = getToolByName(script, 'portal_workflow')

wtool.doActionFor(context, workflow_action, comment=comment)

context.setStatus(True, _(u'Status changed.'))
context.setRedirect(context, 'object/view')
