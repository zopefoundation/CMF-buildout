##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Customizable objects that come from the filesystem (base class).

$Id$
"""

from os import path, stat

import Globals
from AccessControl import ClassSecurityInfo
from AccessControl.Role import RoleManager
from Acquisition import Implicit
from OFS.Cache import Cacheable
from OFS.SimpleItem import Item
from DateTime import DateTime
from Products.PythonScripts.standard import html_quote

from permissions import ManagePortal
from permissions import View
from permissions import ViewManagementScreens
from utils import expandpath
from utils import getToolByName


class FSObject(Implicit, Item, RoleManager, Cacheable):
    """FSObject is a base class for all filesystem based look-alikes.

    Subclasses of this class mimic ZODB based objects like Image and
    DTMLMethod, but are not directly modifiable from the management
    interface. They provide means to create a TTW editable copy, however.
    """

    # Always empty for FS based, non-editable objects.
    title = ''

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    _file_mod_time = 0
    _parsed = 0

    def __init__(self, id, filepath, fullname=None, properties=None):
        if properties:
            # Since props come from the filesystem, this should be
            # safe.
            self.__dict__.update(properties)
            if fullname and properties.get('keep_extension', 0):
                id = fullname

            cache = properties.get('cache')
            if cache:
                self.ZCacheable_setManagerId(cache)

        self.id = id
        self.__name__ = id # __name__ is used in traceback reporting
        self._filepath = filepath
        fp = expandpath(self._filepath)

        try: self._file_mod_time = stat(fp)[8]
        except: pass
        self._readFile(0)

    security.declareProtected(ViewManagementScreens, 'manage_doCustomize')
    def manage_doCustomize(self, folder_path, RESPONSE=None):
        """Makes a ZODB Based clone with the same data.

        Calls _createZODBClone for the actual work.
        """

        obj = self._createZODBClone()

        # Preserve cache manager associations
        cachemgr_id = self.ZCacheable_getManagerId()
        if ( cachemgr_id and 
             getattr(obj, 'ZCacheable_setManagerId', None) is not None ):
            obj.ZCacheable_setManagerId(cachemgr_id)

        id = obj.getId()
        fpath = tuple( folder_path.split('/') )
        portal_skins = getToolByName(self,'portal_skins')
        folder = portal_skins.restrictedTraverse(fpath)
        if id in folder.objectIds():
            # we cant catch the badrequest so
            # we'll that to check before hand
            obj = folder._getOb(id)
            if RESPONSE is not None:
                RESPONSE.redirect('%s/manage_main?manage_tabs_message=%s' % (
                    obj.absolute_url(), html_quote("An object with this id already exists")
                    ))
        else:
            folder._verifyObjectPaste(obj, validate_src=0)
            folder._setObject(id, obj)

            if RESPONSE is not None:
                RESPONSE.redirect('%s/%s/manage_main' % (
                folder.absolute_url(), id))

        if RESPONSE is not None:
            RESPONSE.redirect('%s/%s/manage_main' % (
                folder.absolute_url(), id))

    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        raise NotImplementedError, "This should be implemented in a subclass."

    def _readFile(self, reparse):
        """Read the data from the filesystem.

        Read the file indicated by exandpath(self._filepath), and parse the
        data if necessary.  'reparse' is set when reading the second
        time and beyond.
        """
        raise NotImplementedError, "This should be implemented in a subclass."

    # Refresh our contents from the filesystem if that is newer and we are
    # running in debug mode.
    def _updateFromFS(self):
        parsed = self._parsed
        if not parsed or Globals.DevelopmentMode:
            fp = expandpath(self._filepath)
            try:    mtime=stat(fp)[8]
            except: mtime=0
            if not parsed or mtime != self._file_mod_time:
                # if we have to read the file again, remove the cache
                self.ZCacheable_invalidate()
                self._readFile(1)
                self._file_mod_time = mtime
                self._parsed = 1

    security.declareProtected(View, 'get_size')
    def get_size(self):
        """Get the size of the underlying file."""
        fp = expandpath(self._filepath)
        return path.getsize(fp)

    security.declareProtected(View, 'getModTime')
    def getModTime(self):
        """Return the last_modified date of the file we represent.

        Returns a DateTime instance.
        """
        self._updateFromFS()
        return DateTime(self._file_mod_time)

    security.declareProtected(ViewManagementScreens, 'getObjectFSPath')
    def getObjectFSPath(self):
        """Return the path of the file we represent"""
        self._updateFromFS()
        return self._filepath

Globals.InitializeClass(FSObject)


class BadFile( FSObject ):
    """
        Represent a file which was not readable or parseable
        as its intended type.
    """
    meta_type = 'Bad File'
    icon = 'p_/broken'

    BAD_FILE_VIEW = """\
<dtml-var manage_page_header>
<dtml-var manage_tabs>
<h2> Bad Filesystem Object: &dtml-getId; </h2>

<h3> File Contents </h3>
<pre>
<dtml-var getFileContents>
</pre>

<h3> Exception </h3>
<pre>
<dtml-var getExceptionText>
</pre>
<dtml-var manage_page_footer>
"""

    manage_options=(
        {'label':'Error', 'action':'manage_showError'},
        )

    def __init__( self, id, filepath, exc_str=''
                , fullname=None, properties=None):
        id = fullname or id # Use the whole filename.
        self.exc_str = exc_str
        self.file_contents = ''
        FSObject.__init__(self, id, filepath, fullname, properties)

    security = ClassSecurityInfo()

    showError = Globals.HTML( BAD_FILE_VIEW )
    security.declareProtected(ManagePortal, 'manage_showError')
    def manage_showError( self, REQUEST ):
        """
        """
        return self.showError( self, REQUEST )

    security.declarePrivate( '_readFile' )
    def _readFile( self, reparse ):
        """Read the data from the filesystem.

        Read the file indicated by exandpath(self._filepath), and parse the
        data if necessary.  'reparse' is set when reading the second
        time and beyond.
        """
        try:
            fp = expandpath(self._filepath)
            file = open(fp, 'rb')
            try:
                data = self.file_contents = file.read()
            finally:
                file.close()
        except:  # No errors of any sort may propagate
            data = self.file_contents = None #give up
        return data

    security.declarePublic( 'getFileContents' )
    def getFileContents( self ):
        """
            Return the contents of the file, if we could read it.
        """
        return self.file_contents

    security.declarePublic( 'getExceptionText' )
    def getExceptionText( self ):
        """
            Return the exception thrown while reading or parsing
            the file.
        """
        return self.exc_str

Globals.InitializeClass( BadFile )
