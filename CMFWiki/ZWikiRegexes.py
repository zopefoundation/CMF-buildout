import re

#international (latin?) characters
intl_char_entities = (
    ('\300', '&Agrave;'),     #�#<--char
    ('\302', '&Acirc;'),      #�#
    ('\311', '&Eacute;'),     #�#
    ('\312', '&Ecirc;'),      #�#
    ('\316', '&Icirc;'),      #�#
    ('\324', '&Ocirc;'),      #�#
    ('\333', '&Ucirc;'),      #�#
    ('\340', '&agrave;'),     #�#
    ('\342', '&acirc;'),      #�#
    ('\347', '&ccedil;'),     #�#
    ('\350', '&egrave;'),     #�#
    ('\351', '&eacute;'),     #�#
    ('\352', '&ecirc;'),      #�#
    ('\356', '&icirc;'),      #�#
    ('\364', '&ocirc;'),      #�#
    ('\371', '&ugrave;'),     #�#
    ('\373', '&ucirc;'),      #�#
)
urlchars          = (r'[A-Za-z0-9/:@_%~#=&\.\-\?]+')
url               = (r'["=]?((http|https|ftp|mailto|file|about):%s)'
                     % (urlchars))
urlexp            = re.compile(url)
# trying to co-exist with stx references:
bracketedexpr     = r'\[([^\]0-9][^]]*)\]'
bracketedexprexp  = re.compile(bracketedexpr)
underlinedexpr    = r'_([^_]+)_'
underlinedexprexp = re.compile(underlinedexpr)
wikiname1         = r'\b[A-Z]+[a-z~]+[A-Z0-9][A-Z0-9a-z~]*'
wikiname2         = r'\b[A-Z][A-Z0-9]+[a-z~][A-Z0-9a-z~]*'
simplewikilinkexp = re.compile(r'!?(%s|%s)' % (wikiname1, wikiname2))

wikiending        = r"[ \t\n\r\f\v:;.,<)!?']"
urllinkending     = r'[^A-Za-z0-9/:@_%~\.\-\?]'
wikilink          = (r'!?(%s%s|%s%s|%s|%s%s)'
                    % (wikiname1,wikiending,
                       wikiname2,wikiending,
                       bracketedexpr,url,urllinkending))
wikilinkexp       = re.compile(wikilink)
wikilink_         = r'!?(%s|%s|%s|%s)' % \
                     (wikiname1,wikiname2,bracketedexpr,url)
interwikilinkexp  = re.compile(r'!?((?P<local>%s):(?P<remote>[\w]+))'
                              % (wikilink_))
remotewikiurlexp  = re.compile(r'(?m)RemoteWikiURL[:\s]*(.*)$')
protected_lineexp = re.compile(r'(?m)^!(.*)$')

antidecaptext     = '<!--antidecapitationkludge-->\n'
antidecapexp      = re.compile(antidecaptext)

commentsdelim = "<hr solid id=comments_below>"
preexp = re.compile(r'<pre>')
unpreexp = re.compile(r'</pre>')
citedexp = re.compile(r'^\s*>')
# Match group 1 is citation prefix, group 2 is leading whitespace:
cite_prefixexp = re.compile('([\s>]*>)?([\s]*)')
