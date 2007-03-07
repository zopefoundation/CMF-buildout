## Script (Python) "validatePassword"
##parameters=password='', confirm='', **kw
##title=
##
from Products.CMFCore.utils import getToolByInterfaceName

ptool = getToolByInterfaceName('Products.CMFCore.interfaces.IPropertiesTool')
rtool = getToolByInterfaceName('Products.CMFCore.interfaces.IRegistrationTool')

if ptool.getProperty('validate_email'):
    password = rtool.generatePassword()
    return context.setStatus(True, password=password)
else:
    result = rtool.testPasswordValidity(password, confirm)
    if result:
        return context.setStatus(False, result)
    else:
        return context.setStatus(True)
