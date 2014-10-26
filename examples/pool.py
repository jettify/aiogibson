import asyncio
from aiogibson import create_pool


loop = asyncio.get_event_loop()


@asyncio.coroutine
def go():
    pool = yield from create_pool('/tmp/gibson.sock', minsize=5, maxsize=10,
                                  loop=loop)

    with (yield from pool) as gibson:
        yield from gibson.set('foo', 'bar')
        value = yield from gibson.get('foo')
        print(value)

    pool.clear()

loop.run_until_complete(go())
