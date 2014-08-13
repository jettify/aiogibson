.. highlight:: python
.. module:: aioredis.commands

Getting started
===============

**aiogibson** is a library for accessing a gibson_ cache database
from the asyncio_ (PEP-3156/tulip) framework.

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
        # get value
        result = yield from gibson.get(b'foo')
        print(result)
        # delete value
        yield from gibson.delete(b'foo')

    loop.run_until_complete(go())
