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

from zope.app import zapi

from Products.GenericSetup.interfaces import IBody

from Products.CMFCore.utils import getToolByName

_FILENAME = 'mailhost.xml'


def importMailHost(context):
    """Import mailhost settings from an XML file.
    """
    site = context.getSite()
    logger = context.getLogger('mailhost')
    tool = getToolByName(site, 'MailHost')

    body = context.readDataFile(_FILENAME)
    if body is None:
        logger.info('Nothing to import.')
        return

    importer = zapi.queryMultiAdapter((tool, context), IBody)
    if importer is None:
        logger.warning('Import adapter misssing.')
        return

    importer.body = body

def exportMailHost(context):
    """Export mailhost settings as an XML file.
    """
    site = context.getSite()
    logger = context.getLogger('mailhost')
    tool = getToolByName(site, 'MailHost', None)
    if tool is None:
        logger.info('Nothing to export.')
        return

    exporter = zapi.queryMultiAdapter((tool, context), IBody)
    if exporter is None:
        logger.warning('Export adapter misssing.')
        return

    context.writeDataFile(_FILENAME, exporter.body, exporter.mime_type)
