##parameters=change='', change_and_view=''
##
from Products.CMFDefault.utils import Message as _

form = context.REQUEST.form
if change and \
        context.validateTextFile(**form) and \
        context.validateHTML(**form) and \
        context.document_edit_control(**form) and \
        context.setRedirect(context, 'object/edit'):
    return
elif change_and_view and \
        context.validateTextFile(**form) and \
        context.validateHTML(**form) and \
        context.document_edit_control(**form) and \
        context.setRedirect(context, 'object/view'):
    return


options = {}

options['SafetyBelt'] = form.get('SafetyBelt', context.SafetyBelt())
options['title'] = context.Title()
options['description'] = context.Description()
options['text_format'] = form.get('text_format', context.text_format)
options['text'] = form.get('text', context.EditableBody())

buttons = []
target = context.getActionInfo('object/edit')['url']
buttons.append( {'name': 'change', 'value': _(u'Change')} )
buttons.append( {'name': 'change_and_view', 'value': _(u'Change and View')} )
options['form'] = { 'action': target,
                    'listButtonInfos': tuple(buttons) }

return context.document_edit_template(**options)
