## Script (Python) "wiki_editcomment_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE
##title=
##

text = None
type = None
title = ''
mode = None
comment = None
log = None
ack_requested = None
timeStamp = REQUEST.get('timeStamp', None)

if REQUEST.has_key('comment'):
    comment = REQUEST['comment']
    ack_requested = REQUEST.get('ack_requested', None)
    context.comment(comment, ack_requested)
else:
    text = REQUEST['text']
    log = REQUEST.get('log', '')
    context.edit(text=text,type=type, title=title,log=log,timeStamp=timeStamp)

RESPONSE.redirect('%s' % context.wiki_page_url())
