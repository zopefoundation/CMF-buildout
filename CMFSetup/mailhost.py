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

$Id: mailhost.py 36704 2004-12-14 20:56:58Z yuppie $
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
_FILENAME = 'mailhost.xml'

def importMailHost( context ):

    """ Import mailhost settings from an XML file.
    """
    site = context.getSite()
    encoding = context.getEncoding()

    if context.shouldPurge():
        # steps to follow to remove old settings
        pass

    text = context.readDataFile( _FILENAME )

    if text is not None:

        mhc = MailHostImportConfigurator( site, encoding )
        mh_info = mhc.parseXML( text )

        # now act on the settings we've retrieved
        mh = getToolByName(site, 'MailHost')

        mh.smtp_host = mh_info['smtp_host']
        mh.smtp_port = mh_info['smtp_port']
        mh.smtp_uid = mh_info['smtp_uid']
        mh.smtp_pwd = mh_info['smtp_pwd']

    return 'Mailhost settings imported.'


def exportMailHost( context ):

    """ Export mailhost properties as an XML file
    """
    site = context.getSite()
    mhc = MailHostExportConfigurator( site ).__of__( site )
    text = mhc.generateXML()

    context.writeDataFile( _FILENAME, text, 'text/xml' )

    return 'MailHost properties exported.'


class MailHostExportConfigurator(ExportConfiguratorBase):
    """ Synthesize XML description of mailhost properties.
    """
    security = ClassSecurityInfo()

    security.declareProtected( ManagePortal, 'getMailHostInfo' )
    def getMailHostInfo( self ):
        """ List the valid role IDs for our site.
        """
        mh = getToolByName(self._site, 'MailHost')

        config = {}
        config['id'] = mh.getId()
        config['smtp_host'] = mh.smtp_host
        config['smtp_port'] = int(mh.smtp_port)
        config['smtp_uid'] = getattr(mh, 'smtp_uid', '')
        config['smtp_pwd'] = getattr(mh, 'smtp_pwd', '')
        config['i18n_domain'] = ''

        return config

    def _getExportTemplate(self):

        return PageTemplateFile('mhcExport.xml', _xmldir)

InitializeClass(MailHostExportConfigurator)


class MailHostImportConfigurator(ImportConfiguratorBase):

    def _getImportMapping(self):

        return {
          'mailhost':
            { 'i18n:domain':{},
              'id':         {},
              'smtp_host':  {},
              'smtp_port':  {},
              'smtp_uid':   {},
              'smtp_pwd':   {},
              'xmlns:i18n': {} },
          }

InitializeClass(MailHostImportConfigurator)

# BBB: will be removed in CMF 1.7
class MailHostConfigurator(MailHostImportConfigurator
                          ,MailHostExportConfigurator
                          ):

    def __init__(self, site, encoding=None):
        MailHostImportConfigurator.__init__(self, site, encoding=None)
        MailHostExportConfigurator.__init__(self, site, encoding=None)

InitializeClass(MailHostConfigurator)


