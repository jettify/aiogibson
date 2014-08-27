.. aiogibson documentation master file, created by
   sphinx-quickstart on Wed Aug  6 21:33:43 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to aiogibson's documentation!
=====================================

**aiogibson** is a library for accessing a gibson_ cache database
from the asyncio_ (PEP-3156/tulip) framework.

Gibson is a high efficiency, tree based memory cache server.
It uses a special trie_ structure allowing the
user to perform operations on multiple key sets using a prefix
expression achieving the same performance grades in the worst case,
even better on an average case then regular cache implementations
based on hash tables.


Contents:

.. toctree::
   :maxdepth: 2


Installation
------------

The easiest way to install *aiogibson* is by using the package on PyPi::

   pip install aiogibson



Contribute
----------

- Issue Tracker: https://github.com/jettify/aiogibson/issues
- Source Code: https://github.com/jettify/aiogibson

Feel free to file an issue or make pull request if you find any bugs or have
some suggestions for library improvement.



Contents
========

.. toctree::
   :maxdepth: 3

   start
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _MIT license: https://github.com/jettify/aiogibson/blob/master/LICENSE
.. _Python: https://www.python.org
.. _asyncio: http://docs.python.org/3.4/library/asyncio.html
.. _gibson: http://gibson-db.in/
.. _aioredis: https://github.com/aio-libs/aioredis
.. _trie: http://en.wikipedia.org/wiki/Trie
