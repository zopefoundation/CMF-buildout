##parameters=
##title=Delete reply
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import Message as _

dtool = getToolByName(script, 'portal_discussion')

parent = context.inReplyTo()
talkback = dtool.getDiscussionFor(parent)
talkback.deleteReply( context.getId() )

context.setStatus(True, _(u'Reply deleted.'))
context.setRedirect(parent, 'object/view')
