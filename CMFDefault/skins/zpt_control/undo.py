##parameters=transaction_info
##title=Undo transactions
##
from Products.CMFCore.utils import getToolByInterfaceName
from Products.CMFDefault.utils import Message as _

utool = getToolByInterfaceName('Products.CMFCore.interfaces.IUndoTool')

utool.undo(context, transaction_info)

context.setStatus(True, _(u'Transaction(s) undone.'))
context.setRedirect(context, 'object/folderContents')
