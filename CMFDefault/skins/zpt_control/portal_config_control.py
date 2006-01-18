##parameters=**kw
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import Message as _

ptool = getToolByName(script, 'portal_properties')

if not ptool.hasProperty('default_charset'):
    ptool.manage_addProperty('default_charset', '', 'string')
ptool.editProperties(kw)

return context.setStatus(True, _('CMF Settings changed.'))
