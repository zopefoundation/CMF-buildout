##parameters=member=None, password='baz'
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
member_address = member and member.email or 'foo@example.org'
options['member_address'] = '<%s>' % member_address
options['content_type'] = 'text/plain; charset=%s' % default_charset

options['portal_title'] = ptool.title()
options['password'] = password

rendered = context.member_password_mail_template(**decode(options, script))
if isinstance(rendered, unicode):
    return rendered.encode(default_charset)
else:
    return rendered
