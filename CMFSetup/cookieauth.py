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
"""Cookie crumbler setup handlers.

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


def importCookieCrumbler(context):
    """ Import cookie crumbler settings from an XML file.
    """
    site = context.getSite()

    if context.shouldPurge():
        # steps to follow to remove old settings
        pass

    body = context.readDataFile(_FILENAME)
    if body is None:
        return 'Cookie crumbler: Nothing to import.'

    # now act on the settings we've retrieved
    cc = site.cookie_authentication
    ccc = CookieCrumblerImportConfigurator(site)
    cc_info = ccc.parseXML(body)

    for prop_info in cc_info['properties']:
        ccc.initProperty(cc, prop_info)

    return 'Cookie crumbler settings imported.'

def exportCookieCrumbler(context):
    """ Export cookie crumbler settings as an XML file.
    """
    site = context.getSite()
    mhc = CookieCrumblerExportConfigurator( site ).__of__( site )
    text = mhc.generateXML()

    context.writeDataFile( _FILENAME, text, 'text/xml' )

    return 'Cookie crumbler settings exported.'


class CookieCrumblerExportConfigurator(ExportConfiguratorBase):
    """ Synthesize XML description of cc properties.
    """
    security = ClassSecurityInfo()

    security.declareProtected( ManagePortal, 'getCookieCrumblerInfo' )
    def getCookieCrumblerInfo(self):
        """ List the valid role IDs for our site.
        """
        cc = self._site.cookie_authentication
        properties = tuple( [ self._extractProperty(cc, prop_map)
                              for prop_map in cc._propertyMap() ] )
        return {'id': cc.getId(), 'properties': properties}

    def _getExportTemplate(self):

        return PageTemplateFile('ccExport.xml', _xmldir)

InitializeClass(CookieCrumblerExportConfigurator)


class CookieCrumblerImportConfigurator(ImportConfiguratorBase):

    def _getImportMapping(self):
        return {}

InitializeClass(CookieCrumblerImportConfigurator)
