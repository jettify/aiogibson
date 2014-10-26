import asyncio
from aiogibson import create_gibson


loop = asyncio.get_event_loop()


@asyncio.coroutine
def go():
    gibson = yield from create_gibson('/tmp/gibson.sock', loop=loop)
    # set value
    yield from gibson.set(b'foo', b'bar', 7)
    # get value
    result = yield from gibson.get(b'foo')
    print(result)
    # delete value
    yield from gibson.delete(b'foo')

loop.run_until_complete(go())


