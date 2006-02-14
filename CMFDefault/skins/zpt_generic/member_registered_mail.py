##parameters=tool=None, request=None, member=None, password='baz', email='foo@example.org', **kw
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import decode

atool = getToolByName(script, 'portal_actions')
ptool = getToolByName(script, 'portal_properties')
utool = getToolByName(script, 'portal_url')
default_charset = ptool.getProperty('default_charset')
portal_url = utool()


options = {}

email_from_name = ptool.getProperty('email_from_name')
email_from_address = ptool.getProperty('email_from_address')
options['portal_address'] = '%s <%s>' % (email_from_name, email_from_address)
options['member_address'] = '<%s>' % email
options['content_type'] = 'text/plain; charset=%s' % default_charset

options['portal_title'] = ptool.title()
options['portal_description'] = ptool.getProperty('description')
options['portal_url'] = portal_url

member_id = member and member.getId() or 'foo'
options['member_id'] = member_id
options['password'] = password

target = atool.getActionInfo('user/login')['url']
options['login_url'] = '%s' % target
options['signature'] = email_from_name

rendered = context.member_registered_mail_template(**decode(options, script))
if isinstance(rendered, unicode):
    return rendered.encode(default_charset)
else:
    return rendered
