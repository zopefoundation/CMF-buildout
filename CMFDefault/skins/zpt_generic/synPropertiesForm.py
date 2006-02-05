##parameters=
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import decode

stool = getToolByName(script, 'portal_syndication')


options = {}

s_site_allowed = stool.isSiteSyndicationAllowed()
s_here_allowed = stool.isSyndicationAllowed(context)

options['title'] = context.Title()
options['description'] = context.Description()
options['s_site_allowed'] = s_site_allowed
options['s_here_allowed'] = s_here_allowed
options['s_allowed'] = s_site_allowed and s_here_allowed
options['s_tool'] = stool

return context.synPropertiesForm_template(**decode(options, script))
