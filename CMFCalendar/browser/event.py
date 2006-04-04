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
"""Browser views for events.

$Id$
"""

from DateTime.DateTime import DateTime

from Products.CMFDefault.exceptions import ResourceLockedError
from Products.CMFCalendar.utils import Message as _

from Products.CMFDefault.browser.utils import decode
from Products.CMFDefault.browser.utils import FormViewBase
from Products.CMFDefault.browser.utils import memoize
from Products.CMFDefault.browser.utils import ViewBase


class EventView(ViewBase):

    """View for IEvent.
    """

    # interface

    @memoize
    @decode
    def contact_name(self):
        return self.context.contact_name

    @memoize
    @decode
    def location(self):
        return self.context.location

    @memoize
    @decode
    def contact_email(self):
        return self.context.contact_email

    @memoize
    @decode
    def event_types(self):
        return self.context.Subject()

    @memoize
    @decode
    def contact_phone(self):
        return self.context.contact_phone

    @memoize
    @decode
    def event_url(self):
        return self.context.event_url

    @memoize
    @decode
    def start_date(self):
        return DateTime(self.context.start()).Date()

    @memoize
    @decode
    def start_time(self):
        return DateTime(self.context.start()).Time()

    @memoize
    @decode
    def stop_date(self):
        return DateTime(self.context.end()).Date()

    @memoize
    @decode
    def stop_time(self):
        return DateTime(self.context.end()).Time()


class EventEditView(FormViewBase):

    """Edit view for IMutableEvent.
    """

    _BUTTONS = ({'id': 'change',
                 'title': _(u'Change'),
                 'transform': ('edit_control',),
                 'redirect': ('portal_types', 'object/edit')},
                {'id': 'change_and_view',
                 'title': _(u'Change and View'),
                 'transform': ('edit_control',),
                 'redirect': ('portal_types', 'object/view')})

    # interface

    @memoize
    @decode
    def title(self):
        form = self.request.form
        return form.get('title', None) or self.context.Title()

    @memoize
    @decode
    def description(self):
        form = self.request.form
        return form.get('description', None) or self.context.Description()

    @memoize
    @decode
    def contact_name(self):
        form = self.request.form
        return form.get('contact_name', None) or self.context.contact_name

    @memoize
    @decode
    def location(self):
        form = self.request.form
        return form.get('location', None) or self.context.location

    @memoize
    @decode
    def contact_email(self):
        form = self.request.form
        return form.get('contact_email', None) or self.context.contact_email

    @memoize
    @decode
    def event_type(self):
        form = self.request.form
        return form.get('event_type', None) or self.context.Subject()

    @memoize
    @decode
    def contact_phone(self):
        form = self.request.form
        return form.get('contact_phone', None) or self.context.contact_phone

    @memoize
    @decode
    def event_url(self):
        form = self.request.form
        return form.get('event_url', None) or self.context.event_url

    @memoize
    @decode
    def start_time(self):
        start_string = self.request.form.get('start_time', None)

        if start_string is None:
            start_string = self.context.getStartTimeString().split()[0]

        return start_string

    @memoize
    @decode
    def startAMPM(self):
        start_ampm = self.request.form.get('startAMPM', None)

        if start_ampm is None:
            time_strings = self.context.getStartTimeString().split()
            start_ampm = (len(time_strings) == 2 and time_strings[1] or 'pm')

        return start_ampm

    @memoize
    @decode
    def stop_time(self):
        stop_string = self.request.form.get('stop_time', None)

        if stop_string is None:
            stop_string = self.context.getStopTimeString().split()[0]

        return stop_string

    @memoize
    @decode
    def stopAMPM(self):
        stop_ampm = self.request.form.get('stopAMPM', None)

        if stop_ampm is None:
            time_strings = self.context.getStopTimeString().split()
            stop_ampm = (len(time_strings) == 2 and time_strings[1] or 'pm')

        return stop_ampm

    @memoize
    @decode
    def effectiveYear(self):
        eff_year = self.request.form.get('effectiveYear', None)

        return eff_year or self.context.getStartStrings()['year']

    @memoize
    @decode
    def effectiveMo(self):
        eff_month = self.request.form.get('effectiveMo', None)

        return eff_month or self.context.getStartStrings()['month']

    @memoize
    @decode
    def effectiveDay(self):
        eff_day = self.request.form.get('effectiveDay', None)

        return eff_day or self.context.getStartStrings()['day']

    @memoize
    @decode
    def expirationYear(self):
        exp_year = self.request.form.get('expirationYear', None)

        return exp_year or self.context.getEndStrings()['year']

    @memoize
    @decode
    def expirationMo(self):
        exp_month = self.request.form.get('expirationMo', None)

        return exp_month or self.context.getEndStrings()['month']

    @memoize
    @decode
    def expirationDay(self):
        exp_day = self.request.form.get('expirationDay', None)

        return exp_day or self.context.getEndStrings()['day']

    # controllers

    def edit_control( self
                    , title=None
                    , description=None
                    , event_type=None
                    , effectiveDay=None
                    , effectiveMo=None
                    , effectiveYear=None
                    , expirationDay=None
                    , expirationMo=None
                    , expirationYear=None
                    , start_time=None
                    , startAMPM=None
                    , stop_time=None
                    , stopAMPM=None
                    , location=None
                    , contact_name=None
                    , contact_email=None
                    , contact_phone=None
                    , event_url=None
                    , **kw
                    ):

        try:
            self.context.edit( title, description, event_type, effectiveDay
                             , effectiveMo, effectiveYear, expirationDay
                             , expirationMo, expirationYear, start_time
                             , startAMPM, stop_time, stopAMPM, location
                             , contact_name, contact_email, contact_phone
                             , event_url)
            return True, _(u'Event changed.')
        except ResourceLockedError, errmsg:
            return False, errmsg
