##parameters=title, text, **kw
##title=Reply to content
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import Message as _

dtool = getToolByName(script, 'portal_discussion')

talkback = dtool.getDiscussionFor(context)
replyID = talkback.createReply(title=title, text=text)
reply = talkback.getReply(replyID)

context.setStatus(True, _(u'Reply added.'))
context.setRedirect(reply, 'object/view')
