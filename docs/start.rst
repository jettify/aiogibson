.. highlight:: python
.. module:: aioredis.commands

Getting started
===============

The easiest way to install **aiogibson** is by using the package on PyPi::

   pip install aiogibson

Make sure that gibson server installed and started according official
documentation_. We assume that you have your *gibson* started using
unix sockets (by default) with address ``/tmp/aiogibson.sock``, your ``python``
version >= 3.3.

**aiogibson** has straightforward api, just like *memcached*:


Simple Example
--------------

.. code:: python

    import asyncio
    from aiogibson import create_gibson

    loop = asyncio.get_event_loop()


    @asyncio.coroutine
    def go():
        # create gibson connection
        gibson = yield from create_gibson('/tmp/aiogibson.sock', loop=loop)
        # set value with key ``foo``, value ``bar`` with ``ttl`` 7 seconds
        yield from gibson.set(b'foo', b'bar', 7)
        # get previously set value:
        result = yield from gibson.get(b'foo')
        # delete previously set value
        yield from gibson.delete(b'foo')

    loop.run_until_complete(go())





Long Example
------------

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

        # return list of keys with given prefix ``fo``
        yield from gibson.keys(b'fo')

        # Get system stats about the Gibson instance
        info = yield from gibson.stats()


    loop.run_until_complete(go())

.. _documentation: http://gibson-db.in/download/
