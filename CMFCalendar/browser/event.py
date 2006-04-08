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
        title = self.request.form.get('title', None)

        if title is None:
            title = self.context.Title()

        return title

    @memoize
    @decode
    def description(self):
        description = self.request.form.get('description', None)

        if description is None:
            description = self.context.Description()

        return description

    @memoize
    @decode
    def contact_name(self):
        contact_name = self.request.form.get('contact_name', None)

        if contact_name is None:
            contact_name = self.context.contact_name

        return contact_name

    @memoize
    @decode
    def location(self):
        location = self.request.form.get('location', None)

        if location is None:
            location = self.context.location

        return location

    @memoize
    @decode
    def contact_email(self):
        contact_email = self.request.form.get('contact_email', None)

        if contact_email is None:
            contact_email = self.context.contact_email

        return contact_email

    @memoize
    @decode
    def event_type(self):
        event_type = self.request.form.get('event_type', None)

        if event_type is None:
            event_type = self.context.Subject()

        return event_type

    @memoize
    @decode
    def contact_phone(self):
        contact_phone = self.request.form.get('contact_phone', None)

        if contact_phone is None:
            contact_phone = self.context.contact_phone

        return contact_phone

    @memoize
    @decode
    def event_url(self):
        event_url = self.request.form.get('event_url', None)

        if event_url is None:
            event_url = self.context.event_url

        return event_url

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
        effective_year = self.request.form.get('effectiveYear', None)

        if effective_year is None:
            effective_year = self.context.getStartStrings()['year']

        return effective_year

    @memoize
    @decode
    def effectiveMo(self):
        effective_month = self.request.form.get('effectiveMo', None)

        if effective_month is None:
            effective_month = self.context.getStartStrings()['month']

        return effective_month

    @memoize
    @decode
    def effectiveDay(self):
        effective_day = self.request.form.get('effectiveDay', None)

        if effective_day is None:
            effective_day = self.context.getStartStrings()['day']

        return effective_day

    @memoize
    @decode
    def expirationYear(self):
        expiration_year = self.request.form.get('expirationYear', None)

        if expiration_year is None:
            expiration_year = self.context.getEndStrings()['year']

        return expiration_year

    @memoize
    @decode
    def expirationMo(self):
        expiration_month = self.request.form.get('expirationMo', None)

        if expiration_month is None:
            expiration_month = self.context.getEndStrings()['month']

        return expiration_month

    @memoize
    @decode
    def expirationDay(self):
        expiration_day = self.request.form.get('expirationDay', None)

        if expiration_day is None:
            expiration_day = self.context.getEndStrings()['day']

        return expiration_day

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

