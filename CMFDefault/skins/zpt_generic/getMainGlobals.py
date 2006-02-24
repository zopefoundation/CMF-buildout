##parameters=
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import decode

atool = getToolByName(script, 'portal_actions')
mtool = getToolByName(script, 'portal_membership')
ptool = getToolByName(script, 'portal_properties')
utool = getToolByName(script, 'portal_url')
wtool = getToolByName(script, 'portal_workflow')
portal_object = utool.getPortalObject()

default_charset = ptool.getProperty('default_charset', None)
if default_charset:
    context.REQUEST.RESPONSE.setHeader('Content-Type',
                                     'text/html;charset=%s' % default_charset)

message = context.REQUEST.get('portal_status_message')
if message and isinstance(message, str):
    message = message.decode(default_charset)

globals = {'utool': utool,
           'mtool': mtool,
           'atool': atool,
           'wtool': wtool,
           'portal_object': portal_object,
           'portal_title': portal_object.Title(),
           'object_title': context.Title(),
           'object_description': context.Description(),
           'portal_url': utool(),
           'member': mtool.getAuthenticatedMember(),
           'membersfolder': mtool.getMembersFolder(),
           'isAnon': mtool.isAnonymousUser(),
           'wf_state': wtool.getInfoFor(context, 'review_state', ''),
           'status_message': message}

return decode(globals, context)
