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
"""ContentTypeRegistry setup handlers.

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
_FILENAME = 'contenttyperegistry.xml'

def importContentTypeRegistry(context):
    """ Import content type registry settings from an XML file.
    """
    site = context.getSite()
    ctr = getToolByName(site, 'content_type_registry', None)
    if ctr is None:
        return 'Content type registry: No tool!'

    body = context.readDataFile(_FILENAME)
    if body is None:
        return 'Content type registry: Nothing to import.'

    if context.shouldPurge():
        ctr.__init__()

    # now act on the settings we've retrieved
    configurator = ContentTypeRegistryImportConfigurator(site)
    cpm_info = configurator.parseXML(body)

    for info in cpm_info['predicates']:
        ctr.addPredicate(info['predicate_id'], info['predicate_type'])
        arguments = [x['value'].encode('ascii') for x in info['arguments']]
        ctr.getPredicate(info['predicate_id']).edit(*arguments)
        ctr.assignTypeName(info['predicate_id'], info['content_type_name'])

    return 'Content type registry settings imported.'

def exportContentTypeRegistry(context):
    """ Export content type registry settings as an XML file.
    """
    site = context.getSite()
    mhc = ContentTypeRegistryExportConfigurator( site ).__of__( site )
    text = mhc.generateXML()

    context.writeDataFile( _FILENAME, text, 'text/xml' )

    return 'Content type registry settings exported.'


class ContentTypeRegistryExportConfigurator(ExportConfiguratorBase):
    """ Synthesize XML description of ctr properties.
    """
    security = ClassSecurityInfo()

    security.declareProtected( ManagePortal, 'listPredicateInfo' )
    def listPredicateInfo(self):
        """ Return a list of mappings describing the tool's predicates.
        """
        cpm = getToolByName(self._site, 'content_type_registry')
        for predicate_id, (predicate,
                           content_type_name) in cpm.listPredicates():
            yield {'predicate_id': predicate_id,
                   'predicate_type': predicate.PREDICATE_TYPE,
                   'content_type_name' : content_type_name,
                   'arguments' : self._crackArgs(predicate),
                  }

    _KNOWN_PREDICATE_TYPES = {
        'major_minor': lambda x: (','.join(x.major), ','.join(x.minor)),
        'extension': lambda x: (','.join(x.extensions),),
        'mimetype_regex': lambda x: (x.pattern and x.pattern.pattern,),
        'name_regex': lambda x: (x.pattern and x.pattern.pattern,),
    }

    security.declarePrivate('_crackArgs')
    def _crackArgs(self, predicate):
        """ Crack apart the "edit args" from predicate.
        """
        cracker = self._KNOWN_PREDICATE_TYPES.get(predicate.PREDICATE_TYPE)
        if cracker is not None:
            return cracker(predicate)
        return ()  # XXX:  raise?
        
    security.declarePrivate('_getExportTemplate')
    def _getExportTemplate(self):

        return PageTemplateFile('ctrExport.xml', _xmldir)

InitializeClass(ContentTypeRegistryExportConfigurator)

class ContentTypeRegistryImportConfigurator(ImportConfiguratorBase):

    def _getImportMapping(self):
        return {
          'content-type-registry':
             { 'predicate':             {KEY: 'predicates', DEFAULT: ()}
             },
          'predicate':
             { 'predicate_id':          {},
               'remove':                {},
               'predicate_type':        {},
               'content_type_name':     {},
               'argument':              {KEY: 'arguments', DEFAULT: ()},
             },
           'argument':
             { 'value':                 {},
             },
          }

InitializeClass(ContentTypeRegistryImportConfigurator)
