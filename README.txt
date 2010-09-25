=================
CMF dev buildouts
=================
--------------------------------
Build CMF 2.2 + Zope 2.12 branch
--------------------------------

Introduction
============

Builds CMF 2.2 from develop eggs located in ``src``. This buildout is usually
used for developing CMF 2.2 on its primary target platform: Zope 2.12 branch
and five.localsitemanager trunk.

Dependencies
============

Requires Python 2.6

Usage
=====
::

  $ python2.6 bootstrap.py
  $ ./bin/buildout
  $ ./bin/test
  $ ./bin/instance

---------------------------------
Build CMF 2.2 + Zope 2.13 release
---------------------------------

Introduction
============

Builds CMF 2.2 from develop eggs located in ``src``. This buildout is usually
used for testing CMF 2.2 on a different platform: The latest Zope 2.13 and
five.localsitemanager 2.0 releases.

Dependencies
============

Requires Python 2.6

Usage
=====
::

  $ python2.6 bootstrap.py
  $ ./bin/buildout -c buildout-zope213.cfg
  $ ./bin/test
