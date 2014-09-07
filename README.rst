aiogibson
=========

.. image:: https://travis-ci.org/jettify/aiogibson.svg?branch=master
   :target: https://travis-ci.org/jettify/aiogibson
   :alt: |Build status|
.. image:: https://pypip.in/v/aiogibson/badge.svg
   :target: https://pypi.python.org/pypi/aiogibson/
   :alt: |Latest PyPI version|
.. image:: https://pypip.in/d/aiogibson/badge.svg
   :target: https://pypi.python.org/pypi/aiogibson/
   :alt: |Number of PyPI downloads|
.. image:: https://pypip.in/license/aiogibson/badge.svg
    :target: https://pypi.python.org/pypi/aiogibson/
    :alt: |License|


**aiogibson** is a library for accessing a gibson_ cache database
from the asyncio_ (PEP-3156/tulip) framework.

Gibson is a high efficiency, tree based memory cache server.
It uses a special trie_ structure allowing the
user to perform operations on multiple key sets using a prefix
expression achieving the same performance grades in the worst case,
even better on an average case then regular cache implementations
based on hash tables.


Code heavily reused from awesome aioredis_ library. ``GibsonPool``,
``GibsonConnection``, almost direct copy of ``RedisPool`` and
``RedisConnection``, so I highly recommend to checkout aioredis_.

Example
-------

.. code:: python

    import asyncio
    from aiogibson import create_gibson

    loop = asyncio.get_event_loop()


    @asyncio.coroutine
    def go():
        gibson = yield from create_gibson('/tmp/aio.sock', loop=loop)
        # set value
        yield from gibson.set(b'foo', b'bar', 7)
        yield from gibson.set(b'numfoo', 100, 7)

        # get value
        result = yield from gibson.get(b'foo')
        print(result)

        # set ttl to the value
        yield from gibson.ttl(b'foo', 10)

        # increment given key
        yield from gibson.inc(b'numfoo')

        # decrement given key
        yield from gibson.dec(b'numfoo')

        # lock key from modification
        yield from gibson.lock(b'numfoo')

        # unlock given key
        yield from gibson.unlock(b'numfoo')

        # fetch keys with given prefix
        yield from gibson.keys(b'foo')

        # delete value
        yield from gibson.delete(b'foo')


    loop.run_until_complete(go())

Underlying data structure trie_ allows us to perform operations on multiple
key sets using a prefix expression:


Multi Commands
--------------

.. code:: python

    import asyncio
    from aiogibson import create_gibson

    loop = asyncio.get_event_loop()


    @asyncio.coroutine
    def go():
        gibson = yield from create_gibson('/tmp/aio.sock', loop=loop)

        # set the value for keys verifying the given prefix
        yield from gibson.mset(b'fo', b'bar', 7)
        yield from gibson.mset(b'numfo', 100, 7)

        # get the values for keys with given prefix
        result = yield from gibson.mget(b'fo')

        # set the TTL for keys verifying the given prefix
        yield from gibson.mttl(b'fo', 10)

        # increment by one keys verifying the given prefix.
        yield from gibson.minc(b'numfo')

        # decrement by one keys verifying the given prefix
        yield from gibson.mdec(b'numfoo')

        # lock keys with prefix from modification
        yield from gibson.mlock(b'fo')

        # unlock keys with given prefix
        yield from gibson.munlock(b'fo')

        # delete keys verifying the given prefix.
        yield from gibson.mdelete(b'fo')

        # return list of keys with given prefix ``fo``
        yield from gibson.keys(b'fo')

        # count items for a given prefi
        info = yield from gibson.stats()


    loop.run_until_complete(go())

**aiogibson** has connection pooling support using context-manager:


Connection Pool Example
-----------------------

.. code:: python

    import asyncio
    from aiogibson import create_pool

    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def go():
        pool = yield from create_pool('/tmp/aio.sock', minsize=5, maxsize=10,
                                      loop=loop)

        with (yield from pool) as gibson:
            yield from gibson.set('foo', 'bar')
            value = yield from gibson.get('foo')
            print(value)

        pool.clear()

    loop.run_until_complete(go())


Also you can have simple low-level interface to *gibson* server:


Low Level Commands
------------------

.. code:: python

    import asyncio
    from aiogibson import create_gibson

    loop = asyncio.get_event_loop()


    @asyncio.coroutine
    def go():
        gibson = yield from create_connection('/tmp/aio.sock', loop=loop)

        # set value
        yield from gibson.execute(b'set', b'foo', b'bar', 7)

        # get value
        result = yield from gibson.execute(b'get', b'foo')
        print(result)
        # delete value
        yield from gibson.execute(b'del', b'foo')


    loop.run_until_complete(go())


Requirements
------------

* Python_ 3.3+
* asyncio_ or Python_ 3.4+


License
-------

The *aiogibson* is offered under MIT license.

.. _Python: https://www.python.org
.. _asyncio: http://docs.python.org/3.4/library/asyncio.html
.. _gibson: http://gibson-db.in/
.. _aioredis: https://github.com/aio-libs/aioredis
.. _trie: http://en.wikipedia.org/wiki/Trie
