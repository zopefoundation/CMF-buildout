## Script (Python) "newsitem_edit"
##parameters=text, description, text_format=None, change_and_view=''
##title=Edit a news item
try:
    from Products.CMFDefault.utils import scrubHTML
    text = scrubHTML( text ) # Strip Javascript, etc.
    description = scrubHTML( description )
 
    context.edit(text=text, description=description, text_format=text_format)

    qst='portal_status_message=News+Item+changed.'

    if change_and_view:
        target_action = context.getTypeInfo().getActionById( 'view' )
    else:
        target_action = context.getTypeInfo().getActionById( 'edit' )

    context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                    , target_action
                                                    , qst
                                                    ) )
except Exception, msg:
    target_action = context.getTypeInfo().getActionById( 'edit' )
    context.REQUEST.RESPONSE.redirect(
        '%s/%s?portal_status_message=%s' % ( context.absolute_url()
                                           , target_action
                                           , msg
                                           ) )
