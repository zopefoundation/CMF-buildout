##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
""" Event: A CMF-enabled Event object.

$Id$
"""

import os, urllib
from DateTime import DateTime
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFCore.PortalContent import PortalContent, NoWL, ResourceLockedError
from Products.CMFCore.WorkflowCore import WorkflowAction

# Import permission names
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from Products.CMFDefault.utils import formatRFC822Headers, html_headcheck
from Products.CMFDefault.utils import SimpleHTMLParser, bodyfinder, parseHeadersBody
from Products.CMFCore.utils import keywordsplitter

import EventPermissions

# Factory type information -- makes Events objects play nicely
# with the Types Tool (portal_types)
factory_type_information = (
    {'id': 'Event',
     'content_icon': 'event_icon.gif',
     'meta_type': 'CMF Event',
     'description': ('Events are objects for use in Calendar topical '
                     'queries on the catalog.'),
     'product': 'CMFCalendar',
     'factory': 'addEvent',
     'immediate_view': 'event_edit_form',
     'actions': ({'id': 'view',
                  'name': 'View',
                  'action': 'string:event_view',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'Edit',
                  'action': 'string:event_edit_form',
                  'permissions': (EventPermissions.ChangeEvents,)},
                 ),                     # End Actions
     },
    )

def addEvent(self
             , id
             , title=''
             , description=''
             , effective_date = None 
             , expiration_date = None 
             , start_date = None 
             , end_date = None
             , location=''
             , contact_name=''
             , contact_email=''
             , contact_phone=''
             , event_url=''
             , REQUEST=None):
    """
    Create an empty event.
    """
    event = Event(id
                  , title
                  , description
                  , effective_date
                  , expiration_date
                  , start_date
                  , end_date
                  , location
                  , contact_name
                  , contact_email
                  , contact_phone
                  , event_url
                 )
    self._setObject(id, event)

def _dateStrings( when ):

    strings = {}

    if when is not None:
        strings[ 'year' ]   = str( when.year() )
        strings[ 'month' ]  = str( when.month() )
        strings[ 'day' ]    = str( when.day() )
    else:
        strings[ 'year' ]   = ''
        strings[ 'month' ]  = ''
        strings[ 'day' ]    = ''

    return strings

class Event(PortalContent, DefaultDublinCoreImpl):
    """
    Events are objects for the Calendar topical query.
    """
    meta_type='CMF Event'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)
    
    __implements__ = ( PortalContent.__implements__
                     , DefaultDublinCoreImpl.__implements__
                     )

    def __init__(self
                 , id
                 , title=''
                 , description=''
                 , effective_date = None 
                 , expiration_date = None 
                 , start_date = None
                 , end_date = None
                 , location=''
                 , contact_name=''
                 , contact_email=''
                 , contact_phone=''
                 , event_url=''
                ):
        DefaultDublinCoreImpl.__init__(self)
        self.id=id
        self.setTitle(title)
        self.setDescription(description)
        self.effective_date = effective_date
        self.expiration_date = expiration_date
        self.setStartDate(start_date)

        if start_date is None:
            start_date = DateTime()
        if end_date is None:
            end_date = start_date
        
        if end_date < start_date:
            end_date = start_date

        self.setEndDate(end_date)
        self.location=location
        self.contact_name=contact_name
        self.contact_email=contact_email
        self.contact_phone=contact_phone
        self.event_url=event_url

    security.declarePrivate( '_datify' )
    def _datify( self, attrib ):
        if attrib == 'None':
            attrib = None
        elif not isinstance( attrib, DateTime ):
            if attrib is not None:
                attrib = DateTime( attrib )
        return attrib
    
    security.declarePublic('getEndStrings')
    def getEndStrings(self):
        """
        """
        return _dateStrings(self.end())

    security.declarePublic('getStartStrings')
    def getStartStrings(self):
        """
        """
        return _dateStrings(self.start())

    security.declareProtected(EventPermissions.ChangeEvents, 'edit')
    def edit(self
             , title=None
             , description=None
             , eventType=None
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
            ):
        """\
        """
        
        if title is not None: 
            self.setTitle(title)
        if description is not None:
            self.setDescription(description)
        if eventType is not None:
            self.setSubject(eventType)

        start_date = end_date = None

        if effectiveDay and effectiveMo and effectiveYear and start_time:
            efdate = '%s/%s/%s %s %s' % (effectiveDay
                                         , effectiveMo
                                         , effectiveYear
                                         , start_time
                                         , startAMPM
                                         )
            start_date = DateTime( efdate )

        if expirationDay and expirationMo and expirationYear and stop_time:

            exdate = '%s/%s/%s %s %s' % (expirationDay
                                         , expirationMo
                                         , expirationYear
                                         , stop_time
                                         , stopAMPM
                                         )
            end_date = DateTime( exdate )
        
        if start_date and end_date:

            if end_date < start_date:
                end_date = start_date
 
            self.setStartDate( start_date )
            self.setEndDate( end_date )

        if location is not None:
            self.location = location
        if contact_name is not None:
            self.contact_name = contact_name
        if contact_email is not None:
            self.contact_email = contact_email
        if contact_phone is not None:
            self.contact_phone = contact_phone
        if event_url is not None:
            self.event_url = event_url
        self.reindexObject()
    edit = WorkflowAction(edit) 
    
    security.declarePublic('buildTimes')
    def buildTimes(self):
        result = []
        for hour in range (1, 13):
            for min in (00, 30):
                result.append('%02d:%02d' % (hour, min))
        return result
    
    security.declarePublic('buildDays')
    def buildDays(self):
        result = []
        for day in range (1, 32):
            result.append(str('%d' % (day)))
        return result

    security.declarePublic('buildMonths')
    def buildMonths(self):
        result = []
        for month in range (1, 13):
            result.append(str('%d' % (month)))
        return result
    
    security.declarePublic('buildYears')
    def buildYears(self):
        result = []
        start = (DateTime().year() - 2)
        end = (DateTime().year() + 5)
        for year in range (start, end):
            result.append(str(year))
        return result

    security.declareProtected(EventPermissions.ChangeEvents, 'setStartDate')
    def setStartDate(self, start):
        """
        Setting the event start date, when the event is scheduled to begin.
        """
        self.start_date = self._datify(start)
    
    security.declareProtected(EventPermissions.ChangeEvents, 'setEndDate')
    def setEndDate(self, end):
        """
        Setting the event end date, when the event ends.
        """
        self.end_date = self._datify(end)

    security.declarePublic('start')
    def start(self):
        """
            Return our start time as a string.
        """
        date = getattr( self, 'start_date', None )
        return date is None and self.created() or date

    security.declarePublic('end')
    def end(self):
        """
            Return our stop time as a string.
        """
        date = getattr( self, 'end_date', None )
        return date is None and self.start() or date    

    security.declarePublic('getStartTimeString')
    def getStartTimeString( self ):
        """
            Return our start time as a string.
        """
        return self.start().AMPMMinutes() 

    security.declarePublic('getStopTimeString')
    def getStopTimeString( self ):
        """
            Return our stop time as a string.
        """
        return self.end().AMPMMinutes() 

    security.declarePrivate('handleText')
    def handleText(self, text, format=None):
        """ Handles the raw text, returning headers, body, cooked, format """
        headers = {}
        if format == 'html':
            parser = SimpleHTMLParser()
            parser.feed(text)
            headers.update(parser.metatags)
            if parser.title:
                headers['Title'] = parser.title
            bodyfound = bodyfinder(text)
            if bodyfound:
                body = bodyfound
        else:
            headers, body = parseHeadersBody(text, headers)

        return headers, body, format

    security.declareProtected(ModifyPortalContent, 'setMetadata')
    def setMetadata(self, headers):
        headers['Format'] = self.Format()
        new_subject = keywordsplitter(headers)
        headers['Subject'] = new_subject or self.Subject()
        haveheader = headers.has_key
        for key, value in self.getMetadataHeaders():
            if key != 'Format' and not haveheader(key):
                headers[key] = value
        self._editMetadata(title=headers['Title'],
                          subject=headers['Subject'],
                          description=headers['Description'],
                          contributors=headers['Contributors'],
                          effective_date=headers['Effective_date'],
                          expiration_date=headers['Expiration_date'],
                          format=headers['Format'],
                          language=headers['Language'],
                          rights=headers['Rights'],
                          )
 
    security.declarePublic( 'getMetadataHeaders' )
    def getMetadataHeaders(self):
        """Return RFC-822-style header spec."""
        hdrlist = DefaultDublinCoreImpl.getMetadataHeaders(self)
        hdrlist.append( ('StartDate', self.start().strftime("%Y-%m-%d %H:%M:%S") ) )
        hdrlist.append( ('EndDate',  self.end().strftime("%Y-%m-%d %H:%M:%S") ) )
        hdrlist.append( ('Location', self.location) )
        hdrlist.append( ('ContactName', self.contact_name) )
        hdrlist.append( ('ContactEmail', self.contact_email) )
        hdrlist.append( ('ContactPhone', self.contact_phone) )
        hdrlist.append( ('EventURL', self.event_url) )

        return hdrlist

    ## FTP handlers
    security.declareProtected(ModifyPortalContent, 'PUT')

    def PUT(self, REQUEST, RESPONSE):
        """ Handle HTTP (and presumably FTP?) PUT requests """
        if not NoWL:
            self.dav__init(REQUEST, RESPONSE)
            self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
        body = REQUEST.get('BODY', '')
        guessedformat = REQUEST.get_header('Content-Type', 'text/plain')
        ishtml = (guessedformat == 'text/html') or html_headcheck(body)

        if ishtml: self.setFormat('text/html')
        else: self.setFormat('text/plain')

        try:
            headers, body, format = self.handleText(text=body)
            self.setMetadata(headers)
            self.setStartDate(headers['StartDate'])
            self.setEndDate(headers['EndDate'])
            self.edit( location=headers['Location']
             , contact_name=headers['ContactName']
             , contact_email=headers['ContactEmail']
             , contact_phone=headers['ContactPhone']
             , event_url=headers['EventURL']
             )
            
        except ResourceLockedError, msg:
            get_transaction().abort()
            RESPONSE.setStatus(423)
            return RESPONSE

        RESPONSE.setStatus(204)
        self.reindexObject()
        return RESPONSE

    security.declareProtected(View, 'manage_FTPget')
    def manage_FTPget(self):
        "Get the document body for FTP download (also used for the WebDAV SRC)"
        hdrlist = self.getMetadataHeaders()
        hdrtext = formatRFC822Headers( hdrlist )
        bodytext = '%s\r\n\r\n%s' % ( hdrtext, self.Description() )

        return bodytext

    security.declareProtected(View, 'get_size')
    def get_size( self ):
        """ Used for FTP and apparently the ZMI now too """
        return len(self.manage_FTPget())

# Intialize the Event class, setting up security.
InitializeClass(Event)
