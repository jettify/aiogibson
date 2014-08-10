aiogibson
=========
.. image:: https://travis-ci.org/jettify/aiogibson.svg?branch=master
   :target: https://travis-ci.org/jettify/aiogibson

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

Requirements
------------

* Python_ 3.3+
* asyncio_ or Python_ 3.4+


Other Python client
-------------------

* https://github.com/bak1an/pygibson


License
-------

The *aiogibson* is offered under MIT license.

.. _Python: https://www.python.org
.. _asyncio: http://docs.python.org/3.4/library/asyncio.html
.. _gibson: http://gibson-db.in/
.. _aioredis: https://github.com/aio-libs/aioredis
