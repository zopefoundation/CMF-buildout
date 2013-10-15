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
