##parameters=member=None, password='secret'
##
from Products.CMFCore.utils import getToolByInterfaceName
from Products.CMFDefault.utils import decode
from Products.CMFDefault.utils import makeEmail
from Products.CMFDefault.utils import Message as _

atool = getToolByInterfaceName('Products.CMFCore.interfaces.IActionsTool')
ptool = getToolByInterfaceName('Products.CMFCore.interfaces.IPropertiesTool')
utool = getToolByInterfaceName('Products.CMFCore.interfaces.IURLTool')
portal_url = utool()


options = {}
options['password'] = password

headers = {}
headers['Subject'] = _(u'${portal_title}: Membership reminder',
                      mapping={'portal_title': decode(ptool.title(), script)})
headers['From'] = '%s <%s>' % (ptool.getProperty('email_from_name'),
                               ptool.getProperty('email_from_address'))
headers['To'] = '<%s>' % (member and member.email or 'foo@example.org')

mtext = context.password_email_template(**decode(options, script))
return makeEmail(mtext, script, headers)
