## Script (Python) "expanded_title"
##parameters=
##title=Build title which includes site title
##
from Products.CMFCore.utils import getToolByInterfaceName
from Products.CMFDefault.utils import decode

utool = getToolByInterfaceName('Products.CMFCore.interfaces.IURLTool')

site_title = utool.getPortalObject().Title()
page_title = context.Title()

if page_title != site_title:
   page_title = site_title + ": " + page_title

return decode(page_title, script)
