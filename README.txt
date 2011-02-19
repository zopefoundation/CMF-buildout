=================
CMF dev buildouts
=================
--------------------------
Build CMF 2.3 + Zope trunk
--------------------------

Introduction
============

Builds CMF 2.3 from develop eggs located in ``src``. This buildout is usually
used for developing CMF 2.3 on its primary target platform: Zope trunk and
five.localsitemanager trunk.

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
Build CMF 2.3 + Zope 2.13 release
---------------------------------

Introduction
============

Builds CMF 2.3 from develop eggs located in ``src``. This buildout is usually
used for testing CMF 2.3 on a different platform: The latest Zope 2.13 and
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
