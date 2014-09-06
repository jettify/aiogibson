.. highlight:: python
.. module:: aiogibson.commands

Getting started
===============

The easiest way to install **aiogibson** is by using the package on PyPi::

   pip install aiogibson

Make sure that gibson server installed and started according official
documentation_. We assume that you have your *gibson* started using
unix sockets (by default) with address ``/tmp/aiogibson.sock``, your ``python``
version >= 3.3.

**aiogibson** has straightforward api, just like *memcached*:


Basic Example
-------------

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

        # delete value
        yield from gibson.delete(b'foo')

        # Get system stats about the Gibson instance
        info = yield from gibson.stats()


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



.. _documentation: http://gibson-db.in/download/
.. _trie: http://en.wikipedia.org/wiki/Trie
