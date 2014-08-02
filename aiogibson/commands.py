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

    @property
    def closed(self):
        """True if connection is closed."""
        return self._conn.closed

    @asyncio.coroutine
    def get(self, key):
        return (yield from self._conn.execute(b'get', key))

    @asyncio.coroutine
    def set(self, key, value, expire=0):
        return (yield from self._conn.execute(b'set', expire, key, value))

    @asyncio.coroutine
    def delete(self, key):
        return (yield from self._conn.execute(b'del', key))

    @asyncio.coroutine
    def ttl(self, key, expire):
        return (yield from self._conn.execute(b'ttl', key, expire))

    @asyncio.coroutine
    def inc(self, key):
        return (yield from self._conn.execute(b'inc', key))

    @asyncio.coroutine
    def dec(self, key):
        return (yield from self._conn.execute(b'dec', key))

    @asyncio.coroutine
    def lock(self, key, expire=0):
        result = yield from self._conn.execute(b'lock', key, expire)
        return result

    @asyncio.coroutine
    def unlock(self, key):
        result = yield from self._conn.execute(b'unlock', key)
        return result

    @asyncio.coroutine
    def keys(self, prefix):
        result = yield from self._conn.execute(b'keys', prefix)
        return result

    @asyncio.coroutine
    def stats(self):
        result = yield from self._conn.execute(b'stats')
        return result

    @asyncio.coroutine
    def ping(self):
        return (yield from self._conn.execute(b'ping'))

    def meta_size(self, key):
        # size: The size in bytes of the item value.
        return (yield from self._conn.execute(b'meta', key, b'size'))

    def meta_encoding(self, key):
        # encoding: The value encoding.
        return (yield from self._conn.execute(b'meta', key, b'encoding'))

    def meta_access(self, key):
        # access: Timestamp of the last time the item was accessed.
        return (yield from self._conn.execute(b'meta', key, b'access'))

    def meta_created(self, key):
        # created: Timestamp of item creation.
        return (yield from self._conn.execute(b'meta', key, b'created'))

    def meta_ttl(self, key):
        # ttl: Item specified time to live, -1 for infinite TTL.

        return (yield from self._conn.execute(b'meta', key,  b'ttl'))

    def meta_left(self, key):
        # left: Number of seconds left for the item to live if a ttl
        #  was specified, otherwise -1.
        return (yield from self._conn.execute(b'meta', key, b'left'))

    def meta_lock(self, key):
        # lock: Number of seconds the item is locked, -1 if there's no lock.
        return (yield from self._conn.execute(b'meta', key, b'lock'))

    def end(self):
        return (yield from self._conn.execute(b'end'))

    @asyncio.coroutine
    def mset(self, prefix, value):
        return (yield from self._conn.execute(b'mset', prefix, value))

    @asyncio.coroutine
    def mget(self, prefix):
        return (yield from self._conn.execute(b'mget', prefix))

    @asyncio.coroutine
    def mttl(self, prefix, expire):
        return (yield from self._conn.execute(b'mttl', prefix, expire))

    @asyncio.coroutine
    def minc(self, prefix):
        return (yield from self._conn.execute(b'minc', prefix))

    @asyncio.coroutine
    def mdec(self, prefix):
        return (yield from self._conn.execute(b'mdec', prefix))

    @asyncio.coroutine
    def mlock(self, prefix, expire=0):
        result = yield from self._conn.execute(b'mlock', prefix, expire)
        return result

    @asyncio.coroutine
    def munlock(self, prefix):
        result = yield from self._conn.execute(b'munlock', prefix)
        return result

    @asyncio.coroutine
    def mdelete(self, prefix):
        result = yield from self._conn.execute(b'mdel', prefix)
        return result

    @asyncio.coroutine
    def count(self, prefix):
        """Count items for a given prefix.

        :param prefix:
        :return: ``int`` number of elements
        """
        return (yield from self._conn.execute(b'count', prefix))


@asyncio.coroutine
def create_gibson(address, *, encoding=None, commands_factory=Gibson,
                  loop=None):
    """Creates high-level Gibson interface.
    """
    conn = yield from create_connection(address, encoding=encoding, loop=loop)
    return commands_factory(conn)
