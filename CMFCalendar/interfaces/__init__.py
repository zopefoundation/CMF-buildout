##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFCalendar.interfaces package.

$Id$
"""

from _content import *
from _tools import *

# BBB: will be removed in CMF 2.2
#      create zope2 interfaces
from Interface.bridge import createZope3Bridge
import Event
import portal_calendar

createZope3Bridge(IEvent, Event, 'IEvent')
createZope3Bridge(IMutableEvent, Event, 'IMutableEvent')
createZope3Bridge(ICalendarTool, portal_calendar, 'portal_calendar')

del createZope3Bridge
