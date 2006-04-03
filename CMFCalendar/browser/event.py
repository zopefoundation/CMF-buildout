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
from Products.CMFDefault.utils import Message as _

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
        return self.request.form.get('title', self.context.Title())

    @memoize
    @decode
    def description(self):
        return self.request.form.get('description', self.context.Description())

    @memoize
    @decode
    def contact_name(self):
        return self.request.form.get('contact_name', self.context.contact_name)

    @memoize
    @decode
    def location(self):
        return self.request.form.get('location', self.context.location)

    @memoize
    @decode
    def contact_email(self):
        return self.request.form.get( 'contact_email'
                                    , self.context.contact_email
                                    )

    @memoize
    @decode
    def event_type(self):
        return self.request.form.get('event_type', self.context.Subject())

    @memoize
    @decode
    def contact_phone(self):
        return self.request.form.get( 'contact_phone'
                                    , self.context.contact_phone
                                    )

    @memoize
    @decode
    def event_url(self):
        return self.request.form.get('event_url', self.context.event_url)

    @memoize
    @decode
    def start_time(self):
        time_strings = self.context.getStartTimeString().split()
        return self.request.form.get('start_time', time_strings[0])

    @memoize
    @decode
    def startAMPM(self):
        time_strings = self.context.getStartTimeString().split()
        AMPM = (len(time_strings) == 2 and time_strings[1] or 'pm')
        return self.request.form.get('startAMPM', AMPM)

    @memoize
    @decode
    def stop_time(self):
        time_strings = self.context.getStopTimeString().split()
        return self.request.form.get('stop_time', time_strings[0])

    @memoize
    @decode
    def stopAMPM(self):
        time_strings = self.context.getStopTimeString().split()
        AMPM = (len(time_strings) == 2 and time_strings[1] or 'pm')
        return self.request.form.get('stopAMPM', AMPM)

    @memoize
    @decode
    def effectiveYear(self):
        date_strings = self.context.getStartStrings()
        return self.request.form.get('effectiveYear', date_strings['year'])

    @memoize
    @decode
    def effectiveMo(self):
        date_strings = self.context.getStartStrings()
        return self.request.form.get('effectiveMo', date_strings['month'])

    @memoize
    @decode
    def effectiveDay(self):
        date_strings = self.context.getStartStrings()
        return self.request.form.get('effectiveDay', date_strings['day'])

    @memoize
    @decode
    def expirationYear(self):
        date_strings = self.context.getEndStrings()
        return self.request.form.get('expirationYear', date_strings['year'])

    @memoize
    @decode
    def expirationMo(self):
        date_strings = self.context.getEndStrings()
        return self.request.form.get('expirationMo', date_strings['month'])

    @memoize
    @decode
    def expirationDay(self):
        date_strings = self.context.getEndStrings()
        return self.request.form.get('expirationDay', date_strings['day'])

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
