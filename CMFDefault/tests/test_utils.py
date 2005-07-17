from unittest import TestCase, makeSuite, main
import Testing
import Zope
Zope.startup()

from Products.CMFCore.tests.base.content import FAUX_HTML_LEADING_TEXT
from Products.CMFCore.tests.base.content import SIMPLE_HTML
from Products.CMFCore.tests.base.content import SIMPLE_STRUCTUREDTEXT
from Products.CMFCore.tests.base.content import SIMPLE_XHTML
from Products.CMFCore.tests.base.content import STX_WITH_HTML


class DefaultUtilsTests(TestCase):
    COMMON_HEADERS = '''Author: Tres Seaver
Title: Test Products.CMFDefault.utils.parseHeadersBody'''

    MULTILINE_DESCRIPTION = '''Description: this description spans
        multiple lines.'''

    TEST_BODY = '''Body goes here, and can span multiple
lines.  It can even include "headerish" lines, like:

Header: value
'''

    def test_NoBody( self ):
        from Products.CMFDefault.utils import parseHeadersBody

        headers, body = parseHeadersBody( '%s\n\n' % self.COMMON_HEADERS )
        assert( len( headers ) == 2, '%d!' % len( headers ) )
        assert( 'Author' in headers.keys() )
        assert( headers[ 'Author' ] == 'Tres Seaver' )
        assert( 'Title' in headers.keys() )
        assert( len( body ) == 0, '%d!' % len( body ) )

    def test_Continuation( self ):
        from Products.CMFDefault.utils import parseHeadersBody

        headers, body = parseHeadersBody( '%s\n%s\n\n'
                                        % ( self.COMMON_HEADERS
                                          , self.MULTILINE_DESCRIPTION
                                          )
                                        )
        assert( len( headers ) == 3, '%d!' % len( headers )  )
        assert( 'Description' in headers.keys() )
        desc_len = len( headers[ 'Description' ].split('\n') )
        assert( desc_len == 2, '%d!' % desc_len )
        assert( len( body ) == 0, '%d!' % len( body ) )

    def test_Body( self ):
        from Products.CMFDefault.utils import parseHeadersBody

        headers, body = parseHeadersBody( '%s\n\n%s'
                                        % ( self.COMMON_HEADERS
                                          , self.TEST_BODY
                                          )
                                        )
        assert( len( headers ) == 2, '%d!' % len( headers ) )
        assert( body == self.TEST_BODY )

    def test_Preload( self ):
        from Products.CMFDefault.utils import parseHeadersBody

        preloaded = { 'Author' : 'xxx', 'text_format' : 'structured_text' }
        headers, body = parseHeadersBody( '%s\n%s\n\n%s'
                                        % ( self.COMMON_HEADERS
                                          , self.MULTILINE_DESCRIPTION
                                          , self.TEST_BODY
                                          )
                                        , preloaded
                                        )
        assert( len( headers ) == 3, '%d!' % len( headers ) )
        assert( preloaded[ 'Author' ] != headers[ 'Author' ] )
        assert( preloaded[ 'text_format' ] == headers[ 'text_format' ] )

    def test_scrubHTML(self):
        from Products.CMFDefault.utils import scrubHTML

        self.assertEqual( scrubHTML('<a href="foo.html">bar</a>'),
                          '<a href="foo.html">bar</a>' )
        self.assertEqual( scrubHTML('<b>bar</b>'),
                          '<b>bar</b>' )
        self.assertEqual( scrubHTML('<base href="" /><base>'),
                          '<base href="" /><base />' )
        self.assertEqual( scrubHTML('<blockquote>bar</blockquote>'),
                          '<blockquote>bar</blockquote>' )
        self.assertEqual( scrubHTML('<body bgcolor="#ffffff">bar</body>'),
                          '<body bgcolor="#ffffff">bar</body>' )
        self.assertEqual( scrubHTML('<br /><br>'),
                          '<br /><br />' )
        self.assertEqual( scrubHTML('<hr /><hr>'),
                          '<hr /><hr />' )
        self.assertEqual( scrubHTML('<img src="foo.png" /><img>'),
                          '<img src="foo.png" /><img />' )
        self.assertEqual( scrubHTML('<meta name="title" content="" /><meta>'),
                          '<meta name="title" content="" /><meta />' )

    def test_bodyfinder(self):
        from Products.CMFDefault.utils import bodyfinder

        self.assertEqual( bodyfinder(FAUX_HTML_LEADING_TEXT),
                          '\n  <h1>Not a lot here</h1>\n ' )
        self.assertEqual( bodyfinder(SIMPLE_HTML),
                          '\n  <h1>Not a lot here</h1>\n ' )
        self.assertEqual( bodyfinder(SIMPLE_STRUCTUREDTEXT),
                          SIMPLE_STRUCTUREDTEXT )
        self.assertEqual( bodyfinder(SIMPLE_XHTML),
                          '\n  <h1>Not a lot here</h1>\n ' )
        self.assertEqual( bodyfinder(STX_WITH_HTML),
                          '<p>Hello world, I am Bruce.</p>' )

    def test_html_headcheck(self):
        from Products.CMFDefault.utils import html_headcheck

        self.assertEqual( html_headcheck(FAUX_HTML_LEADING_TEXT), 0 )
        self.assertEqual( html_headcheck(SIMPLE_HTML), 1 )
        self.assertEqual( html_headcheck(SIMPLE_STRUCTUREDTEXT), 0 )
        self.assertEqual( html_headcheck(SIMPLE_XHTML), 1 )
        self.assertEqual( html_headcheck(STX_WITH_HTML), 0 )

    def test_tuplize(self):
        from Products.CMFDefault.utils import comma_split
        from Products.CMFDefault.utils import tuplize
        wanted = ('one','two','three')

        self.assertEqual( tuplize('string', 'one two three'), wanted )
        self.assertEqual( tuplize('unicode', u'one two three'), wanted )
        self.assertEqual( tuplize('string', 'one,two,three', comma_split),
                          wanted )
        self.assertEqual( tuplize('list', ['one',' two','three ']), wanted )
        self.assertEqual( tuplize('tuple', ('one','two','three')), wanted )

    def test_seq_strip(self):
        from Products.CMFDefault.utils import seq_strip

        self.assertEqual( seq_strip(['one ', ' two', ' three ']),
                          ['one','two','three'] )
        self.assertEqual( seq_strip(('one ', ' two', ' three ')),
                          ('one','two','three') )

    def test_html_marshal(self):
        from Products.CMFDefault.utils import html_marshal

        self.assertEqual( html_marshal(foo=1), ( ('foo:int', '1'), ) )
        self.assertEqual( html_marshal(foo=1, bar='baz >&baz'),
                          ( ('foo:int', '1'), ('bar', 'baz &gt;&amp;baz') ) )

    def test_toUnicode(self):
        from Products.CMFDefault.utils import toUnicode

        self.assertEqual( toUnicode('foo'), u'foo' )
        self.assertEqual( toUnicode( ('foo', 'bar'), 'ascii' ),
                          (u'foo', u'bar') )
        self.assertEqual( toUnicode( {'foo': 'bar'}, 'iso-8859-1' ),
                          {'foo': u'bar'} )


def test_suite():
    return makeSuite(DefaultUtilsTests)

if __name__ == '__main__':
    main(defaultTest='test_suite')
