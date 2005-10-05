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

from xml.dom.minidom import parseString

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import INodeExporter
from Products.GenericSetup.interfaces import INodeImporter
from Products.GenericSetup.interfaces import PURGE, UPDATE
from Products.GenericSetup.utils import PrettyDocument

_FILENAME = 'mailhost.xml'


def importMailHost(context):
    """ Import mailhost settings from an XML file.
    """
    site = context.getSite()
    mode = context.shouldPurge() and PURGE or UPDATE
    mailhost = getToolByName(site, 'MailHost')

    body = context.readDataFile(_FILENAME)
    if body is None:
        return 'Mailhost: Nothing to import.'

    importer = INodeImporter(mailhost, None)
    if importer is None:
        return 'Mailhost: Import adapter misssing.'

    importer.importNode(parseString(body).documentElement, mode=mode)
    return 'Mailhost settings imported.'

def exportMailHost(context):
    """ Export mailhost settings as an XML file.
    """
    site = context.getSite()

    mailhost = getToolByName(site, 'MailHost', None)
    if mailhost is None:
        return 'Mailhost: Nothing to export.'

    exporter = INodeExporter(mailhost)
    if exporter is None:
        return 'Mailhost: Export adapter misssing.'

    doc = PrettyDocument()
    doc.appendChild(exporter.exportNode(doc))
    context.writeDataFile(_FILENAME, doc.toprettyxml(' '), 'text/xml')
    return 'Mailhost settings exported.'
