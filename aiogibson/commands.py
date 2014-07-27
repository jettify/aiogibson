import asyncio

from .connection import create_connection

__all__ = ['create_gibson', 'Gibson']


class Gibson:
    """XXX"""

    def __init__(self, connection):
        self._conn = connection

    def __repr__(self):
        return '<Gibson {!r}>'.format(self._conn)

    def close(self):
        self._conn.close()

    @asyncio.coroutine
    def get(self, key):
        if not isinstance(key, bytes):
            raise TypeError("key must be instance of bytes")
        result = yield from self._conn.execute(b'get', key)
        # TODO: rethink parser for single value
        return result[0] if result else result

    @asyncio.coroutine
    def set(self, key, value, ttl=0):
        if not isinstance(key, bytes):
            raise TypeError("key must be instance of bytes")
        result = yield from self._conn.execute(b'set', ttl, key, value)
        return result[0]

    @asyncio.coroutine
    def delete(self, key):
        if not isinstance(key, bytes):
            raise TypeError("key must be instance of bytes")
        return (yield from self._conn.execute(b'del', key))

    @asyncio.coroutine
    def ttl(self, key, ttl):
        if not isinstance(key, bytes):
            raise TypeError("key must be instance of bytes")
        return (yield from self._conn.execute(b'ttl', key, ttl))

    @asyncio.coroutine
    def inc(self, key):
        if not isinstance(key, bytes):
            raise TypeError("key must be instance of bytes")
        result = yield from self._conn.execute(b'inc', key)
        return result[0]

    @asyncio.coroutine
    def dec(self, key):
        if not isinstance(key, bytes):
            raise TypeError("key must be instance of bytes")
        result = yield from self._conn.execute(b'dec', key)
        return result[0]

    @asyncio.coroutine
    def ping(self):
        return (yield from self._conn.execute(b'ping'))


@asyncio.coroutine
def create_gibson(address, *, commands_factory=Gibson, loop=None):
    """Creates high-level Gibson interface.
    """
    conn = yield from create_connection(address, loop=loop)
    return commands_factory(conn)
