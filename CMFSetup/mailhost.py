##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Mailhost setup handlers.

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
_FILENAME = 'mailhost.xml'


def importMailHost(context):
    """ Import mailhost settings from an XML file.
    """
    site = context.getSite()

    mailhost = getToolByName(site, 'MailHost')
    if context.shouldPurge():
        # steps to follow to remove old settings
        pass

    body = context.readDataFile(_FILENAME)
    if body is None:
        return 'Mailhost: Nothing to import.'

    mhc = MailHostImportConfigurator(site)
    mh_info = mhc.parseXML(body)

    # now act on the settings we've retrieved
    mailhost.smtp_host = mh_info['smtp_host']
    mailhost.smtp_port = int(mh_info['smtp_port'])
    mailhost.smtp_uid = mh_info['smtp_uid']
    mailhost.smtp_pwd = mh_info['smtp_pwd']

    return 'Mailhost settings imported.'

def exportMailHost(context):
    """ Export mailhost settings as an XML file.
    """
    site = context.getSite()
    mhc = MailHostExportConfigurator( site ).__of__( site )
    text = mhc.generateXML()

    context.writeDataFile( _FILENAME, text, 'text/xml' )

    return 'MailHost settings exported.'


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

        return config

    def _getExportTemplate(self):

        return PageTemplateFile('mhcExport.xml', _xmldir)

InitializeClass(MailHostExportConfigurator)


class MailHostImportConfigurator(ImportConfiguratorBase):

    def _getImportMapping(self):

        return {
          'object':
            { 'name':      {KEY: 'id'},
              'meta_type': {},
              'smtp_host': {},
              'smtp_port': {},
              'smtp_uid':  {},
              'smtp_pwd':  {} } }

InitializeClass(MailHostImportConfigurator)
