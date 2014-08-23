aiogibson
=========

.. image:: https://travis-ci.org/jettify/aiogibson.svg?branch=master
   :target: https://travis-ci.org/jettify/aiogibson
   :alt: Build status
.. image:: https://pypip.in/v/aiogibson/badge.png
   :target: https://pypi.python.org/pypi/aiogibson/
   :alt: Latest PyPI version
.. image:: https://pypip.in/d/aiogibson/badge.png
   :target: https://pypi.python.org/pypi/aiogibson/
   :alt: Number of PyPI downloads



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
