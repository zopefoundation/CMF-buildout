.. caution:: 

    This repository has been archived. If you want to work on it please open a ticket in https://github.com/zopefoundation/meta/issues requesting its unarchival.

=================
CMF dev buildouts
=================

----------------------------
Build CMF trunk + Zope trunk
----------------------------

Introduction
============

Builds CMF trunk from develop eggs located in ``src``. This buildout is usually
used for developing CMF trunk on its primary target platform: Zope trunk and
five.localsitemanager trunk.

Dependencies
============

Requires Python 2.6 or 2.7

Usage
=====
::

  $ python2.7 bootstrap.py
  $ ./bin/buildout
  $ ./bin/test
  $ ./bin/instance

-----------------------------------
Build CMF trunk + Zope 2.13 release
-----------------------------------

Introduction
============

Builds CMF trunk from develop eggs located in ``src``. This buildout is usually
used for testing CMF trunk on a different platform: The latest Zope 2.13 and
five.localsitemanager 2.0 releases.

Dependencies
============

Requires Python 2.6 or 2.7

Usage
=====
::

  $ python2.7 bootstrap.py
  $ ./bin/buildout -c buildout-zope213.cfg
  $ ./bin/test

------------------------------
Experimental Chameleon support
------------------------------

Usage
=====

Just add the five.pt egg to the dependencies. The ``test-with-chameleon``
script tests Chameleon compatibility. Currently this doesn't work on Windows.

Known limitations
=================

- five.pt doesn't work with zope.pagetemplate 4 and Windows newlines

- Issue #144: repeat/item/first/foo seems broken

-------------------------
Experimental WSGI support
-------------------------

Usage
=====

Run ``paster serve`` with a Paste Deploy configuration file like this
``zope2.ini``::

  [server:main]
  use = egg:paste#http
  host = localhost
  port = 8080

  [pipeline:main]
  pipeline =
      egg:paste#evalerror
      egg:repoze.retry#retry
      egg:repoze.tm2#tm
      zope

  [app:zope]
  use = egg:Zope2#main
  zope_conf = path/to/zope.conf

Known limitations
=================

- ``mkzopeinstance`` doesn't generate all the necessary files
