##parameters=change='', change_and_view=''
##
from Products.CMFCalendar.utils import MessageID as _

form = context.REQUEST.form
if change and \
        context.event_edit_control(**form) and \
        context.setRedirect(context, 'object/edit'):
    return
elif change_and_view and \
        context.event_edit_control(**form) and \
        context.setRedirect(context, 'object/view'):
    return


options = {}

buttons = []
target = context.getActionInfo('object/edit')['url']
buttons.append( {'name': 'change', 'value': _('Change')} )
buttons.append( {'name': 'change_and_view', 'value': _('Change and View')} )
options['form'] = { 'action': target,
                    'listButtonInfos': tuple(buttons) }

return context.event_edit_template(**options)
