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

    @memoize
    @decode
    def dayInfo(self):
        """ Event info for a specific day
        """
        info = {}
        caltool = self._getTool('portal_calendar')
        view_url = self._getViewURL()
        date_string = self.request.get('date',DateTime().aCommon()[:12])
        thisDay = DateTime(date_string)

        info['previous_url'] = '%s?date=%s' % (view_url, (thisDay-1).Date())
        info['date'] = thisDay.aCommon()[:12]
        info['next_url'] =  '%s?date=%s' % (view_url, (thisDay+1).Date())
        
        items = [ {'title': item.Title,
                   'url': item.getURL(),
                   'start': self.getStartAsString(thisDay, item),
                   'stop': self.getEndAsString(thisDay, item)}
                  for item in caltool.getEventsForThisDay(thisDay) ]
        
        info['listItemInfos'] = tuple(items)
        
        return info

    @memoize
    @decode
    def getStartAsString(self, day, event):
        """ Retrieve formatted start string
        """
        first_date = DateTime(day.Date()+" 00:00:00")
        
        if event.start < first_date:
            return event.start.aCommon()[:12]
        else:
            return event.start.TimeMinutes()

    @memoize
    @decode
    def getEndAsString(self, day, event):
        """ Retrieve formatted end string
        """
        last_date = DateTime(day.Date()+" 23:59:59")
        
        if event.end > last_date:
            return event.end.aCommon()[:12]
        else:
            return event.end.TimeMinutes()

    @memoize
    @decode
    def getNextDayLink(self, base_url, day):
        """ Return URL for the next day link
        """
        day += 1
        
        return '%s?date=%s' % (base_url, day.Date())

    @memoize
    @decode
    def getPreviousDayLink(self, base_url, day):
        """ Return URL for the previous day link
        """
        day -= 1
        
        return '%s?date=%s' % (base_url, day.Date())

