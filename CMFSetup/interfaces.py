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
""" CMFSetup product interfaces

$Id$
"""

# BBB
from Products.GenericSetup.interfaces import BASE
from Products.GenericSetup.interfaces import EXTENSION
from Products.GenericSetup.interfaces import IPseudoInterface
from Products.GenericSetup.interfaces import ISetupContext
from Products.GenericSetup.interfaces import IImportContext
from Products.GenericSetup.interfaces import IImportPlugin
from Products.GenericSetup.interfaces import IExportContext
from Products.GenericSetup.interfaces import IExportPlugin
from Products.GenericSetup.interfaces import IStepRegistry
from Products.GenericSetup.interfaces import IImportStepRegistry
from Products.GenericSetup.interfaces import IExportStepRegistry
from Products.GenericSetup.interfaces import IToolsetRegistry
from Products.GenericSetup.interfaces import IProfileRegistry
from Products.GenericSetup.interfaces import ISetupTool
