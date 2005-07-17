##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
"""
"""

ADD_CONTENT_PERMISSION = 'Add portal content'

import Globals, string
from Globals import HTMLFile, HTML
from Discussions import Discussable
from AccessControl import ClassSecurityInfo
from Products.CMFCore.PortalContent import PortalContent
from DublinCore import DefaultDublinCoreImpl
from utils import parseHeadersBody, SimpleHTMLParser, bodyfinder

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.WorkflowCore import WorkflowAction, afterCreate

def addDocument(self, id, title='', description='', text_format='',
                text=''):
    """
        Add a Document
    """
    o=Document(id, title, description, text_format, text)
    self._setObject(id,o)
    afterCreate(self.this()._getOb(id))
    

class Document(PortalContent, DefaultDublinCoreImpl):
    """
    A Document
    """

    meta_type = 'Document'
    effective_date = expiration_date = None
    _isDiscussable = 1

    # Declarative security (replaces __ac_permissions__)
    security = ClassSecurityInfo()
    security.declareProtected(CMFCorePermissions.View,
                              'manage_FTPget',
                              'Format', 'Description',)
    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'edit', 'setFormat',)

    def __init__(self, id, title='', description='', text_format='', text=''):
        DefaultDublinCoreImpl.__init__(self)
        self.id=id
        self.title=title
        self.description=description
        self.text=text
        self.text_format=text_format
        self._parse()

    def edit(self, text_format, text, file=''):
        """
            Edit the Document
        """
        self.text = text
        headers = {}
        if file and (type(file) is not type('')):
            contents=file.read()
            if contents:
                text = self.text = contents

        # Now parse out HTML if its applicable, or the plain text,
        # getting any headers passed along in the document
        ishtml = (text_format == 'html') or (string.find(text,'</body>') > -1)
        if ishtml:
            parser = SimpleHTMLParser()
            parser.feed(text)
            headers.update(parser.metatags)
            if parser.title: headers['Title'] = parser.title
            b = bodyfinder.search(text)
            if b: text = self.text = b.group('bodycontent')
            text_format = self.text_format = 'html'
        else:
            headers, text = parseHeadersBody(text, headers)
            text_format = self.text_format = 'structured-text'
            self.text = text

        headers['Format'] = self.Format()
        haveheader = headers.has_key
        for key, value in self.getMetadataHeaders():
            if key != 'Format' and not haveheader(key):
                headers[key] = value
        
        self.editMetadata(title=headers['Title'],
                          subject=headers['Subject'],
                          description=headers['Description'],
                          contributors=headers['Contributors'],
                          effective_date=headers['Effective_date'],
                          expiration_date=headers['Expiration_date'],
                          format=headers['Format'],
                          language=headers['Language'],
                          rights=headers['Rights'],
                          )
        self._parse()
    edit = WorkflowAction(edit)

    def _parse(self):
        if self.text_format=='structured-text':
            ct = self._format_text(text=self.text)
            if type(ct) is not type(''):
                ct = ct.read()
            self.cooked_text=ct
        else:
            self.cooked_text=self.text
            
    _format_text=HTML('''<dtml-var text fmt="structured-text">''')

    def SearchableText(self):
        "text for indexing"
        return "%s %s %s" % (self.title, self.description, self.text)

    def Description(self):
        "description for indexing"
        return self.description
    
    def Format(self):
        """ """
        if self.text_format == 'html':
            return 'text/html'
        else:
            return 'text/plain'
    
    def setFormat(self, value):
        value = str(value)
        if value == 'text/html':
            self.text_format = 'html'
        else:
            self.text_format = 'structured-text'
    setFormat = WorkflowAction(setFormat)

    ## FTP handlers
    def PUT(self, REQUEST, RESPONSE):
        """Handle HTTP (and presumably FTP?) PUT requests"""
        self.dav__init(REQUEST, RESPONSE)
        body = REQUEST.get('BODY', '')
        ishtml = 0
            
        if (REQUEST.get_header('Content-Type', '') == 'text/html') or \
           (string.find(body, '</body>') > -1):
            ishtml = 1

        if ishtml: self.setFormat('text/html')
        else: self.setFormat('text/plain')

        self.edit(text_format=self.text_format, text=body)

        RESPONSE.setStatus(204)
        return RESPONSE

    _htmlsrc = (
        '<html>\n <head>\n'
        ' <title>%(title)s</title>\n'
        ' %(metatags)s'
        ' </head>\n'
        ' <body>\n%(body)s\n </body>\n'
        '</html>\n'
        )

    def manage_FTPget(self):
        "Get the document body for FTP download (also used for the WebDAV SRC)"
        join = string.join
        hdrlist = self.getMetadataHeaders()
        if self.Format() == 'text/html':
            hdrtext = join(map(lambda x: '<meta name="%s" content="%s" />' %(
                x[0], x[1]), hdrlist), '\n')
            bodytext = self._htmlsrc % {
                'title': self.Title(),
                'metatags': hdrtext,
                'body': self.text,
                }
        else:
            hdrtext = join(map(lambda x: '%s: %s' % (
                x[0], x[1]), hdrlist), '\n')
            bodytext = '%s\n\n%s' % ( hdrtext, self.text )

        return bodytext

    def get_size( self ):
        " "
        return len(self.manage_FTPget())

Globals.default__class_init__(Document)

from Products.CMFCore.register import registerPortalContent
registerPortalContent(Document,
                      constructors=(addDocument,),
                      action='Wizards/Document',
                      icon="document.gif",
                      productGlobals=globals())
