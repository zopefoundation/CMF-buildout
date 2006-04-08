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
"""Browser views for the portal calendar.

$Id$
"""

import urlparse

from DateTime.DateTime import DateTime

from Products.CMFDefault.exceptions import ResourceLockedError
from Products.CMFDefault.utils import Message as _

from Products.CMFDefault.browser.utils import decode
from Products.CMFDefault.browser.utils import memoize
from Products.CMFDefault.browser.utils import ViewBase


class CalendarView(ViewBase):

    """ Helper class for calendar-related templates
    """

    @decode
    def getStartAsString(self, event_brain):
        """ Retrieve formatted start string
        """
        day = self.viewDay()
        event_start = event_brain.getObject().start()
        first_date = DateTime(day.Date()+" 00:00:00")
        
        if event_start < first_date:
            return event_start.aCommon()[:12]
        else:
            return event_start.TimeMinutes()

    @decode
    def getEndAsString(self, event_brain):
        """ Retrieve formatted end string
        """
        day = self.viewDay()
        event_end = event_brain.getObject().end()
        last_date = DateTime(day.Date()+" 23:59:59")
        
        if event_end > last_date:
            return event_end.aCommon()[:12]
        else:
            return event_end.TimeMinutes()

    @memoize
    def viewDay(self):
        """ Return a DateTime for a passed-in date or today
        """
        date = self.request.get('date', None) or DateTime().aCommon()[:12]

        return DateTime(date)

    def formattedDate(self):
        """ Return a simple formatted date string
        """
        return self.viewDay().aCommon()[:12]

    def eventsForDay(self):
        """ Get all event catalog records for a specific day
        """
        caltool = self._getTool('portal_calendar')

        return caltool.getEventsForThisDay(self.viewDay())

    @memoize
    def previousDayURL(self):
        """ URL to the previous day's view
        """
        day = self.viewDay()
        view_url = self._getViewURL()

        return '%s?date=%s' % (view_url, (day-1).Date())

    @memoize
    def nextDayURL(self):
        """ URL to the next day's view
        """
        day = self.viewDay()
        view_url = self._getViewURL()

        return '%s?date=%s' % (view_url, (day+1).Date())

    @decode
    def getNextDayLink(self, base_url):
        """ Return URL for the next day link
        """
        day = self.viewDay()
        day += 1
        
        return '%s?date=%s' % (base_url, day.Date())

    @decode
    def getPreviousDayLink(self, base_url):
        """ Return URL for the previous day link
        """
        day = self.viewDay()
        day -= 1
        
        return '%s?date=%s' % (base_url, day.Date())

