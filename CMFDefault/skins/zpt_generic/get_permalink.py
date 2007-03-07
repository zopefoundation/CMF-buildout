## Script (Python) "get_permalink"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Returns the permalink url or None
##
from Products.CMFCore.utils import getToolByInterfaceName

# calculate the permalink if the uid handler tool exists, permalinks
# are configured to be shown and the object is not folderish
uidtool = getToolByInterfaceName( 'Products.CMFUid.interfaces.IUniqueIdHandler'
                                , default=None
                                )

if uidtool is not None:
    ptool = getToolByInterfaceName('Products.CMFCore.interfaces.IPropertiesTool')
    showPermalink = getattr(ptool, 'enable_permalink', None)
    isFolderish = getattr(context.aq_explicit, 'isPrincipiaFolderish', None)
    
    if showPermalink and not isFolderish:
        # returns the uid (generates one if necessary)
        utool = getToolByInterfaceName('Products.CMFCore.interfaces.IURLTool')
        uid = uidtool.register(context)
        url = "%s/permalink/%s" % (utool(), uid)
        return url
