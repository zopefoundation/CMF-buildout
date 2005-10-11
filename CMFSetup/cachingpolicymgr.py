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
"""CachingPolicyManager setup handlers.

$Id$
"""

from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName

from permissions import ManagePortal
from utils import CONVERTER
from utils import DEFAULT
from utils import ExportConfiguratorBase
from utils import ImportConfiguratorBase
from utils import KEY
from utils import _xmldir

#
#   Configurator entry points
#
_FILENAME = 'cachingpolicymgr.xml'

def importCachingPolicyManager(context):
    """ Import cache policy maanger settings from an XML file.
    """
    site = context.getSite()
    cpm = getToolByName(site, 'caching_policy_manager', None)
    if cpm is None:
        return 'Cache policy manager: No tool!'

    body = context.readDataFile(_FILENAME)
    if body is None:
        return 'Cache policy manager: Nothing to import.'

    if context.shouldPurge():
        cpm.__init__()

    # now act on the settings we've retrieved
    configurator = CachingPolicyManagerImportConfigurator(site)
    cpm_info = configurator.parseXML(body)

    for policy in cpm_info['policies']:
        cpm.addPolicy(**policy)

    return 'Cache policy manager settings imported.'

def exportCachingPolicyManager(context):
    """ Export caching policy manager settings as an XML file.
    """
    site = context.getSite()
    mhc = CachingPolicyManagerExportConfigurator( site ).__of__( site )
    text = mhc.generateXML()

    context.writeDataFile( _FILENAME, text, 'text/xml' )

    return 'Caching policy manager settings exported.'

class CachingPolicyManagerExportConfigurator(ExportConfiguratorBase):
    """ Synthesize XML description of cc properties.
    """
    security = ClassSecurityInfo()

    security.declareProtected( ManagePortal, 'listPolicyInfo' )
    def listPolicyInfo(self):
        """ Return a list of mappings describing the tool's policies.
        """
        cpm = getToolByName(self._site, 'caching_policy_manager')
        for policy_id, policy in cpm.listPolicies():
            yield {'policy_id': policy_id,
                   'predicate': policy.getPredicate(),
                   'mtime_func': policy.getMTimeFunc(),
                   'vary': policy.getVary(),
                   'etag_func': policy.getETagFunc(),
                   'max_age_secs': policy.getMaxAgeSecs(),
                   's_max_age_secs': policy.getSMaxAgeSecs(),
                   'pre_check': policy.getPreCheck(),
                   'post_check': policy.getPostCheck(),
                   'last_modified': bool(policy.getLastModified()),
                   'no_cache': bool(policy.getNoCache()),
                   'no_store': bool(policy.getNoStore()),
                   'must_revalidate': bool(policy.getMustRevalidate()),
                   'proxy_revalidate': bool(policy.getProxyRevalidate()),
                   'no_transform': bool(policy.getNoTransform()),
                   'public': bool(policy.getPublic()),
                   'private': bool(policy.getPrivate()),
                   'enable_304s': bool(policy.getEnable304s()),
                  }

    security.declarePrivate('_getExportTemplate')
    def _getExportTemplate(self):

        return PageTemplateFile('cpmExport.xml', _xmldir)

InitializeClass(CachingPolicyManagerExportConfigurator)

class CachingPolicyManagerImportConfigurator(ImportConfiguratorBase):

    def _getImportMapping(self):
        return {
          'caching-policies':
             { 'caching-policy': {KEY: 'policies', DEFAULT: ()} },
          'caching-policy':
             { 'policy_id':         {},
               'remove':            {},
               'predicate':         {},
               'mtime_func':        {},
               'vary':              {},
               'etag_func':         {},
               'max_age_secs':      {CONVERTER: self._convertToInteger},
               's_max_age_secs':    {CONVERTER: self._convertToInteger},
               'pre_check':         {CONVERTER: self._convertToInteger},
               'post_check':        {CONVERTER: self._convertToInteger},
               'last_modified':     {CONVERTER: self._convertToBoolean},
               'no_cache':          {CONVERTER: self._convertToBoolean},
               'no_store':          {CONVERTER: self._convertToBoolean},
               'must_revalidate':   {CONVERTER: self._convertToBoolean},
               'proxy_revalidate':  {CONVERTER: self._convertToBoolean},
               'no_transform':      {CONVERTER: self._convertToBoolean},
               'public':            {CONVERTER: self._convertToBoolean},
               'private':           {CONVERTER: self._convertToBoolean},
               'enable_304s':       {CONVERTER: self._convertToBoolean},
             },
          }

InitializeClass(CachingPolicyManagerImportConfigurator)
