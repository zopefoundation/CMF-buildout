##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" migrateToCMF21.py: Migrate older instances to CMF 2.1

This script must be executed using "zopectl run".

$Id$
"""

from logging import getLogger
import sys
import transaction

logger = getLogger('event.migrateToCMF21')

# The following extensions have a componentregistry.xml import step, and
# the existence of the ID they're mapped to in the portal means the import
# step must be run
AFFECTED_EXTENSIONS = { 
      'Products.CMFCalendar:default' : 'portal_calendar'
    , 'Products.CMFUid:default' : 'portal_uidhandler'
    , 'Products.CMFActionIcons:actionicons' : 'portal_actionicons'
    }

def _log(msg):
    logger.info(msg)
    print msg

def migrate_site(site):
    """ Migrate a single site
    """
    site_path = '/'.join(site.getPhysicalPath())
    _log(' - converting site at %s' % site_path)
    ps = site.portal_setup

    # First we need to run items from the default CMF Site profile

    # Check if we have new-style action providers, if not we need to
    # run the action provider step from CMFDefault:default as well
    if not site.portal_actions.objectIds(['CMF Action Category']):
        steps = ('actions',) # Runs componentregistry as dependency
    else:
        steps = ('componentregistry',)

    ps.setImportContext('profile-Products.CMFDefault:default')
    for step in steps:
        ps.runImportStep(step, run_dependencies=True)

    # Now we go through the extensions that may need to be run
    for extension_id, object_id in AFFECTED_EXTENSIONS.items():
        if object_id in site.objectIds():
            ps.setImportContext('profile-' + extension_id)
            ps.runImportStep('componentregistry', run_dependencies=True)

    _log(' - finished converting site at %s' % site_path)


if __name__ == '__main__':

    _log('Starting CMF migration.')
    
    # First step: Find all instances of CMFSite
    sites = app.ZopeFind(app, obj_metatypes=['CMF Site'], search_sub=1)

    if len(sites) == 0:
        _log('No CMF Site objects found - aborting.')
        sys.exit(1)

    # For every site, grab the portal_setup tool and run the required steps
    for site_id, site in sites:
        migrate_site(site)
        transaction.get().note('Migrated CMF site "%s"' % site_id)
        transaction.commit()

    _log('CMF migration finished.')

