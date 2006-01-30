##parameters=title, text, **kw
##title=Reply to content
##
from Products.CMFCore.utils import getToolByName

dtool = getToolByName(script, 'portal_discussion')
talkback = dtool.getDiscussionFor(context)
replyID = talkback.createReply(title=title, text=text)

target = '%s/%s' % (talkback.absolute_url(), replyID)

context.REQUEST.RESPONSE.redirect(target)
