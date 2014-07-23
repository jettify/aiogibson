import asyncio
import aiogibson

loop = asyncio.get_event_loop()


@asyncio.coroutine
def go():
    conn = yield from aiogibson.create_connection(
        ('localhost', 10128), loop=loop)
    result1 = yield from conn.execute(b'set', b'3600', b'foo1', b'bar1')
    result2 = yield from conn.execute(b'mget', b'fo')
    print(result1, result2)

loop.run_until_complete(go())
