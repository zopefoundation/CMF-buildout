##parameters=
##

from Products.CMFCore.utils import getToolByInterfaceName
from Products.CMFDefault.utils import decode
from Products.CMFDefault.utils import getBrowserCharset

atool = getToolByInterfaceName('Products.CMFCore.interfaces.IActionsTool')
mtool = getToolByInterfaceName('Products.CMFCore.interfaces.IMembershipTool')
ptool = getToolByInterfaceName('Products.CMFCore.interfaces.IPropertiesTool')
utool = getToolByInterfaceName('Products.CMFCore.interfaces.IURLTool')
wtool_iface = 'Products.CMFCore.interfaces.IConfigurableWorkflowTool'
wtool = getToolByInterfaceName(wtool_iface)
portal_object = utool.getPortalObject()

if not 'charset' in context.REQUEST.RESPONSE.getHeader('content-type'):
    # Some newstyle views set a different charset - don't override it.
    # Oldstyle views need the default_charset.
    default_charset = ptool.getProperty('default_charset', None)
    if default_charset:
        context.REQUEST.RESPONSE.setHeader('content-type',
                                    'text/html; charset=%s' % default_charset)

message = context.REQUEST.get('portal_status_message')
if message and isinstance(message, str):
    # portal_status_message uses always the browser charset.
    message = message.decode(getBrowserCharset(context.REQUEST))

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
