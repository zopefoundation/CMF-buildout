##parameters=
##
from Products.CMFCore.utils import getToolByInterfaceName
from Products.CMFDefault.utils import decode
from Products.CMFDefault.utils import Message as _

mtool = getToolByInterfaceName('Products.CMFCore.interfaces.IMembershipTool')
ptool = getToolByInterfaceName('Products.CMFCore.interfaces.IPropertiesTool')
stool = getToolByInterfaceName('Products.CMFCore.interfaces.ISkinsTool')
utool = getToolByInterfaceName('Products.CMFCore.interfaces.IURLTool')
portal_url = utool()


if stool.updateSkinCookie():
    context.setupCurrentSkin()


options = {}

isAnon = mtool.isAnonymousUser()
if isAnon:
    context.REQUEST.RESPONSE.expireCookie('__ac', path='/')
    options['is_anon'] = True
    options['title'] = _(u'Login failure')
    options['admin_email'] = ptool.getProperty('email_from_address')
else:
    mtool.createMemberArea()
    member = mtool.getAuthenticatedMember()
    now = context.ZopeTime()
    last_login = member.getProperty('login_time', None)
    member.setProperties(last_login_time=last_login, login_time=now)
    is_first_login = (last_login == '2000/01/01' and
                      ptool.getProperty('validate_email'))
    if is_first_login:
        member.setProperties(last_login_time='1999/01/01', login_time=now)
        target = '%s/password_form' % portal_url
        context.REQUEST.RESPONSE.redirect(target)
        return
    else:
        member.setProperties(last_login_time=last_login, login_time=now)
        came_from = context.REQUEST.get('came_from', None)
        if came_from:
            context.REQUEST.RESPONSE.redirect(came_from)
            return
        options['is_anon'] = False
        options['title'] = _(u'Login success')

return context.logged_in_template(**decode(options, script))
