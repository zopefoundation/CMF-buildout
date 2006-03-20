##parameters=provider, action_path, **kw
##
from ZTUtils import make_query
from Products.CMFCore.utils import getToolByName

utool = getToolByName(script, 'portal_url')
ptool = getToolByName(script, 'portal_properties')
default_charset = ptool.getProperty('default_charset', None)
portal_url = utool()


try:
    target = provider.getActionInfo(action_path)['url']
except ValueError:
    target = portal_url

message = context.REQUEST.other.get('portal_status_message', '')
if message:
    if isinstance(message, unicode):
        message = unicode(message).encode(default_charset)
    kw['portal_status_message'] = message
for k, v in kw.items():
    if not v:
        del kw[k]

query = kw and ( '?%s' % make_query(kw) ) or ''
context.REQUEST.RESPONSE.redirect( '%s%s' % (target, query) )

return True
