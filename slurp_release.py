#!/usr/bin/python
""" Make a CMF release.
"""

import sys
import os
import httplib
import getopt
import base64
import mimetypes

SVNROOT = 'svn://svn.zope.org/repos/main/CMF'

class ReleasePackage:

    _release_tag = _version_id = _userid = _password = None

    def __init__( self, args ):

        self._parseArgs( args )
        
    #
    #   Packaging API
    #
    def exportReleaseFiles( self ):

        """ Do the Subversion export of CMF for a given release.
        """
        tag_dir = '%s/tags/%s' % (SVNROOT, self._release_tag)
        os.system( 'rm -rf %s' % self._version_id )
        command = ('/usr/bin/env svn export %s %s' % (tag_dir, self._version_id))

        os.system( command )

    def makeArchives( self ):

        """ Create tarball and zipfile for release.
        """
        tar_command = ( '/bin/tar czf %s.tar.gz %s'
                      % ( self._version_id, self._version_id ) )

        zip_command = ( '/usr/bin/zip -r %s.zip %s'
                      % ( self._version_id, self._version_id ) )

        try:
            os.remove( '%s.tar.gz' % self._version_id )
        except OSError:
            pass

        try:
            os.remove( '%s.zip' % self._version_id )
        except OSError:
            pass

        os.system( tar_command )
        os.system( zip_command )

    def uploadArchives( self ):

        """ Upload the tarball / zipfile for the release to the dogbowl.
        """
        tarball  = '%s.tar.gz' % ( self._version_id )
        self._uploadFile( tarball )

        zipfile = '%s.zip' % ( self._version_id )
        self._uploadFile( zipfile )

    def uploadDocs( self ):

        """ Upload the text files for the release to the dogbowl.
        """
        curdir = os.getcwd()
        os.chdir( self._version_id )
        try:
            self._uploadFile( 'CHANGES.txt' )
            self._uploadFile( 'HISTORY.txt' )
            self._uploadFile( 'INSTALL.txt' )
            self._uploadFile( 'LICENSE.txt' )
            self._uploadFile( 'README.txt' )
        finally:
            os.chdir( curdir )

    def doWholeEnchilada( self ):

        """ Run the whole enchilada.
        """
        self.exportReleaseFiles()
        self.makeArchives()
        self.uploadArchives()
        self.uploadDocs()

    def run( self ):
        self._runCommand()
    
    #
    #   Helper methods
    #
    def _usage( self ):

        """ How are we used?
        """
        USAGE = """\
slurp_release [options] version_id

options:

    -?, -h, --help      Print this usage message

    -x, --execute       Select a particular step. Available steps are:

                        exportReleaseFiles
                        makeArchives
                        uploadArchives
                        uploadDocs
                        doWholeEnchilada (default)
    
    -a, --auth          Use authentication pair, in fmt 'userid:password'
"""
        values = {}
        print USAGE % values
        sys.exit( 2 )

    def _parseArgs( self, args ):

        """ Figure out which release, who, etc?
        """
        command = 'doWholeEnchilada'
        try:
            opts, args = getopt.getopt( args
                                      , '?hx:a:'
                                      , [ 'help'
                                        , 'execute='
                                        , 'auth='
                                        ]
                                      )
        except getopt.GetOptError:
            self._usage()

        for k, v in opts:

            if k == '-?' or k == '-h' or k == '--help':
                self._usage()

            if k == '-x' or k == '--execute':
                command = v

            if k == '-a' or k == '--auth':
                self._userid, self._password = v.split( ':' )

        self._command = command

        if len( args ) != 1:
            self._usage()

        self._release_tag = args[0]
        self._version_id = 'CMF-%s' % self._release_tag

    def _runCommand( self ):

        """ Do the specified command.
        """
        getattr( self, self._command )()

    def _getAuthHeaders( self ):

        """ Return the HTTP headers.
        """
        headers = {}
        if self._userid:
            auth = base64.encodestring( '%s:%s'
                                    % ( self._userid, self._password ) )
            headers[ 'Authorization' ] = 'Basic %s' % auth
        return headers

    def _uploadFile( self, filename ):

        """ Upload the zipfile for the release to the dogbowl.
        """
        URL = ( '/Products/CMF/%s/%s' % ( self._version_id, filename ) )
        body = open( filename ).read()
        content_type, content_enc = mimetypes.guess_type(URL)
        headers = self._getAuthHeaders()
        headers['Content-Length'] = len(body)
        headers['Content-Type'] = content_type
        headers['Content-Encoding'] = content_enc

        conn = httplib.HTTPConnection( 'www.zope.org' )
        print 'PUTting file, %s, to URL, %s' % ( filename, URL )

        conn.request( 'PUT', URL, body, headers )
        response = conn.getresponse()
        if int( response.status ) not in ( 200, 201, 204, 302 ):
            raise ValueError, 'Failed: %s (%s)' % ( response.status
                                                  , response.reason )


if __name__ == '__main__':

    import sys

    pkg = ReleasePackage( sys.argv[1:] )

    pkg.run()
