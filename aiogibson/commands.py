import asyncio

from aiogibson.connection import create_connection

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
        return result[0]

    @asyncio.coroutine
    def set(self, key, value, ttl=0):
        if not isinstance(key, bytes):
            raise TypeError("key must be instance of bytes")
        ttl = str(ttl).encode('utf-8')
        return (yield from self._conn.execute(b'get', ttl, key, value))

    @asyncio.coroutine
    def delete(self, key):
        if not isinstance(key, bytes):
            raise TypeError("key must be instance of bytes")
        return (yield from self._conn.execute(b'delete', key))


@asyncio.coroutine
def create_gibson(address, *, db=None, password=None,
                  encoding=None, commands_factory=Gibson,
                  loop=None):
    """Creates high-level Gibson interface.
    """
    conn = yield from create_connection(address, db=db,
                                        password=password,
                                        encoding=encoding,
                                        loop=loop)
    return commands_factory(conn)
