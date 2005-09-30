##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFSetup:  Mailhost import/export

$Id$
"""

from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName

from permissions import ManagePortal
from utils import _xmldir
from utils import ExportConfiguratorBase, ImportConfiguratorBase
from utils import CONVERTER, DEFAULT, KEY


#
#   Configurator entry points
#
_FILENAME = 'cookieauth.xml'

def importCookieCrumbler( context ):

    """ Import cookiecrumbler settings from an XML file.
    """
    site = context.getSite()
    encoding = context.getEncoding()

    if context.shouldPurge():
        # steps to follow to remove old settings
        pass

    text = context.readDataFile( _FILENAME )

    if text is not None:

        ccc = CookieCrumblerImportConfigurator( site, encoding )
        cc_info = ccc.parseXML( text )

        # now act on the settings we've retrieved
        cc = site.cookie_authentication
        props = ccc.parseXML(text)

        cc.auth_cookie = props['auth_cookie']
        cc.name_cookie = props['name_cookie']
        cc.pw_cookie = props['pw_cookie']
        cc.persist_cookie = props['persist_cookie']
        cc.auto_login_page = props['auto_login_page']
        cc.logout_page = props['logout_page']
        cc.unauth_page = props['unauth_page']
        cc.local_cookie_path = props['local_cookie_path']
        cc.cache_header_value = props['cache_header_value']
        cc.log_username = props['log_username']

        return 'Cookie crumbler settings imported.'


def exportCookieCrumbler( context ):

    """ Export cookiecrumbler properties as an XML file
    """
    site = context.getSite()
    mhc = CookieCrumblerExportConfigurator( site ).__of__( site )
    text = mhc.generateXML()

    context.writeDataFile( _FILENAME, text, 'text/xml' )

    return 'CookieCrumbler properties exported.'


class CookieCrumblerExportConfigurator(ExportConfiguratorBase):
    """ Synthesize XML description of cc properties.
    """
    security = ClassSecurityInfo()

    security.declareProtected( ManagePortal, 'getCookieCrumblerInfo' )
    def getCookieCrumblerInfo( self ):
        """ List the valid role IDs for our site.
        """
        cc = self._site.cookie_authentication
        config = {}
        config['auth_cookie'] = cc.auth_cookie
        config['name_cookie'] = cc.name_cookie
        config['pw_cookie'] = cc.pw_cookie
        config['persist_cookie'] = cc.persist_cookie
        config['auto_login_page'] = cc.auto_login_page
        config['logout_page'] = cc.logout_page
        config['unauth_page'] = cc.unauth_page
        config['local_cookie_path'] = cc.local_cookie_path
        config['cache_header_value'] = cc.cache_header_value
        config['log_username'] = cc.log_username
        return config

    def _getExportTemplate(self):

        return PageTemplateFile('ccExport.xml', _xmldir)


InitializeClass(CookieCrumblerExportConfigurator)

class CookieCrumblerImportConfigurator(ImportConfiguratorBase):

    def _getImportMapping(self):

        return {'cookiecrumbler':
                  { 'auth_cookie': {},
                    'name_cookie': {},
                    'pw_cookie': {},
                    'persist_cookie': {},
                    'auto_login_page': {},
                    'logout_page': {},
                    'unauth_page': {},
                    'local_cookie_path': {CONVERTER: self._convertToBoolean},
                    'cache_header_value': {},
                    'log_username': {CONVERTER: self._convertToBoolean},
                  }
               }

InitializeClass(CookieCrumblerImportConfigurator)

# BBB: will be removed in CMF 1.7
class CookieCrumblerConfigurator(CookieCrumblerImportConfigurator,
                                 CookieCrumblerExportConfigurator):
    def __init__(self, site, encoding=None):
        CookieCrumblerImportConfigurator.__init__(self, site, encoding)
        CookieCrumblerExportConfigurator.__init__(self, site, encoding)

InitializeClass(CookieCrumblerConfigurator)

