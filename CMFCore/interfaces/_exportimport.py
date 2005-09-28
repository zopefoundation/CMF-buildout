""" Interfaces for content import / export, based on GenericSetup

$Id$
"""
from zope.interface import Interface
from zope.interface import Attribute

class IFilesystemExporter(Interface):
    """ Plugin interface for site structure export.
    """
    def export(export_context, subdir):
        """ Export our 'context' using the API of 'export_context'.

        o 'export_context' must implement
          Products.GenericSupport.interfaces.IExportContext.

        o 'subdir', if passed, is the relative subdirectory containing our
          context within the site.
        """

    def listExportableItems():
        """ Return a sequence of the child items to be exported.

        o Each item in the returned sequence will be a tuple,
          (id, object, adapter) where adapter must implement
          IFilesystemExporter.
        """

class IFilesystemImporter(Interface):
    """ Plugin interface for site structure export.
    """
    def import_(import_context, subdir):
        """ Import our 'context' using the API of 'import_context'.

        o 'import_context' must implement
          Products.GenericSupport.interfaces.IImportContext.

        o 'subdir', if passed, is the relative subdirectory containing our
          context within the site.
        """

class ICSVAware(Interface):
    """ Interface for objects which dump / load 'text/comma-separated-values'.
    """
    def getId():
        """ Return the Zope id of the object.
        """

    def as_csv():
        """ Return a string representing the object as CSV.
        """

    def put_csv(fd):
        """ Parse CSV and update the object.

        o 'fd' must be a file-like object whose 'read' method returns
          CSV text parseable by the 'csv.reader'.
        """

class IINIAware(Interface):
    """ Interface for objects which dump / load INI-format files..
    """
    def getId():
        """ Return the Zope id of the object.
        """

    def as_ini():
        """ Return a string representing the object as INI.
        """

    def put_ini(stream_or_text):
        """ Parse INI-formatted text and update the object.

        o 'stream_or_text' must be either a string, or else a stream
          directly parseable by ConfigParser.
        """

class IDAVAware(Interface):
    """ Interface for objects which handle their own FTP / DAV operations.
    """
    def getId():
        """ Return the Zope id of the object.
        """

    def manage_FTPget():
        """ Return a string representing the object as a file.
        """

    def PUT(REQUEST, RESPONSE):
        """ Parse file content and update the object.

        o 'REQUEST' will have a 'get' method, which will have the 
          content object in its "BODY" key.  It will also have 'get_header'
          method, whose headers (e.g., "Content-Type") may affect the
          processing of the body.
        """
