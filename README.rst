Work in Progress
================
.. image:: https://travis-ci.org/jettify/aiogibson.svg?branch=master
   :target: https://travis-ci.org/jettify/aiogibson

**aiogibson** is a library for accessing a gibson_ cache database
from the asyncio_ (PEP-3156/tulip) framework.


Example
-------

.. code:: python

    import asyncio
    import aiogibson

    loop = asyncio.get_event_loop()


    @asyncio.coroutine
    def go():
        conn = yield from aiogibson.create_connection(
            ('localhost', 10128), loop=loop)
        result = yield from conn.execute(b'set', 3600, b'foo', b'bar')
        print(result)


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