
import Globals, AccessControl, Products
from AccessControl import Permissions

# General Zope permissions
View = Permissions.view
AccessContentsInformation = Permissions.access_contents_information
UndoChanges = Permissions.undo_changes
ChangePermissions = Permissions.change_permissions
ViewManagementScreens = Permissions.view_management_screens
ManageProperties = Permissions.manage_properties


def setDefaultRoles(permission, roles):
    '''
    Sets the defaults roles for a permission.
    '''
    # XXX This ought to be in AccessControl.SecurityInfo.
    registered = AccessControl.Permission._registeredPermissions
    if not registered.has_key(permission):
        registered[permission] = 1
        Products.__ac_permissions__=(
            Products.__ac_permissions__+((permission,(),roles),))
        mangled = AccessControl.Permission.pname(permission)
        setattr(Globals.ApplicationDefaultPermissions, mangled, roles)

# Note that we can only use the default Zope roles in calls to
# setDefaultRoles().  The default Zope roles are:
# Anonymous, Manager, and Owner.

#
# CMF Base Permissions
#

AccessInactivePortalContent = 'Access inactive portal content'
setDefaultRoles(AccessInactivePortalContent, ('Manager',))

ModifyCookieCrumblers = 'Modify Cookie Crumblers'
setDefaultRoles(ModifyCookieCrumblers, ('Manager',))

ReplyToItem = 'Reply to item'
setDefaultRoles(ReplyToItem, ('Manager',))  # + Member

ManagePortal = 'Manage portal'
setDefaultRoles(ManagePortal, ('Manager',))

ModifyPortalContent = 'Modify portal content'
setDefaultRoles(ModifyPortalContent, ('Manager',))

AddPortalFolders = 'Add portal folders'
setDefaultRoles(AddPortalFolders, ('Owner','Manager'))  # + Member

AddPortalContent = 'Add portal content'
setDefaultRoles(AddPortalContent, ('Owner','Manager',))  # + Member

AddPortalMember = 'Add portal member'
setDefaultRoles(AddPortalMember, ('Anonymous', 'Manager',))

SetOwnPassword = 'Set own password'
setDefaultRoles(SetOwnPassword, ('Manager',))  # + Member

SetOwnProperties = 'Set own properties'
setDefaultRoles(SetOwnProperties, ('Manager',))  # + Member

MailForgottenPassword = 'Mail forgotten password'
setDefaultRoles(MailForgottenPassword, ('Anonymous', 'Manager',))


#
# Workflow Permissions
#

RequestReview = 'Request review'
setDefaultRoles(RequestReview, ('Owner', 'Manager',))

ReviewPortalContent = 'Review portal content'
setDefaultRoles(ReviewPortalContent, ('Manager',))  # + Reviewer

AccessFuturePortalContent = 'Access future portal content'
setDefaultRoles(AccessFuturePortalContent, ('Manager',))  # + Reviewer

