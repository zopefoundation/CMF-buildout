================
CMF Coding Style
================

Here are some CMF specific guidelines. This is an incomplete first cut.

-----------------------
``unicode`` vs. ``str``
-----------------------

Zope 2 and CMF normally use encoded strings. CMF sites have a
``default_charset`` property. All persistent strings edited through the CMF
user interface use the encoding defined in ``default_charset``.

Persistent strings edited through the ZMI might have a different encoding.
Usually only tool settings are edited through the ZMI and tool settings can
always be ASCII strings, so this is not a big issue.

CMF will be migrated to unicode step by step. Recent versions of CMF depend
on some ZTK libraries that expect unicode strings. That made it necessary to
start using unicode in the following areas: PageTemplates, browser views and
i18n messages.

Areas that use unicode have to be separated consequently from areas that use
encoded strings. If you pass encoded strings to PageTemplates and browser views
or if you return unicode from formlib based forms the values have to be
converted:

- For PageTemplates in skins and for normal browser views the ``decode``
  function from ``Products.CMFDefault.utils`` is used.

- Schema adapters are used for formlib based forms. These provide a clean
  interface that returns and accepts only unicode. Don't use any encoded
  strings in form code.

Never write unicode to objects that are implemented for encoded strings.

-----------------------------
``datetime`` vs. ``DateTime``
-----------------------------

Zope 2 and CMF normally use ``DateTime`` objects. These are not the same as
the ``datetime`` objects usually used in Python. But converting them is
possible.

Try to use always offset-naive datetime and DateTime values. Using mixed
values sometimes causes trouble. This is how you can test and normalize them:

    >>> from DateTime.DateTime import DateTime
    >>> local_tz = DateTime().timezone()
    >>> aware_DT = DateTime('2002/02/02 02:02:02 ' + local_tz)
    >>> aware_DT.timezoneNaive()
    False
    >>> aware_dt = aware_DT.asdatetime()
    >>> aware_dt.tzinfo is None
    False

    >>> naive_DT = DateTime(str(aware_DT).rsplit(' ', 1)[0])
    >>> naive_DT.timezoneNaive()
    True
    >>> naive_dt = aware_dt.replace(tzinfo=None)
    >>> naive_dt.tzinfo is None
    True

CMF will be migrated to datetime step by step. Formlib based forms already
require datetime objects. The same schema adapters used for adapting encoded
strings should also be used for adapting DateTime values. Don't use any
DateTime values in form code.

Never write datetime to objects that are implemented for DateTime values.

-------------
upgrade steps
-------------

If your code changes make it necessary to update persistent data, you have to
write an upgrade step that allows to upgrade existing sites in an automated
way without loosing any data.

The current tests only catch changes that are visible in exports of empty
default sites.

=================
Zope Coding Style
=================

See http://docs.zope.org/zopetoolkit/codingstyle/index.html
