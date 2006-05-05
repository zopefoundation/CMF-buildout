##parameters=transaction_info
##title=Undo transactions
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import Message as _

utool = getToolByName(script, 'portal_undo')

utool.undo(context, transaction_info)

context.setStatus(True, _(u'Transaction(s) undone.'))
context.setRedirect(context, 'object/folderContents')
