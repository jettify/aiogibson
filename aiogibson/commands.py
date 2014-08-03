import asyncio

from .connection import create_connection

__all__ = ['create_gibson', 'Gibson']


class Gibson:
    """High-level Gibson interface

    :see: http://gibson-db.in/commands/
    """

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
        """Get the value for a given key.

        :param key: ``bytes``  key to get.
        :return: ``bytes`` if value exists else ``None``
        """
        return (yield from self._conn.execute(b'get', key))

    @asyncio.coroutine
    def set(self, key, value, expire=0):
        """Set the value for the given key, with an optional TTL.

        :param key: ``bytes`` key to set.
        :param value: ``bytes`` value to set.
        :param expire: ``int``  optional ttl in seconds
        """
        return (yield from self._conn.execute(b'set', expire, key, value))

    @asyncio.coroutine
    def delete(self, key):
        """ Delete the given key.

        :param key: ``bytes`` key to delete.
        :return: ``bool`` true in case of success.
        """
        result = (yield from self._conn.execute(b'del', key))
        return bool(result)

    @asyncio.coroutine
    def ttl(self, key, expire):
        """Set the TTL of a key.

        :param key: ``bytes``, key to set ttl.
        :param expire: ``int``, TTL in seconds.
        :return: ``bool``, True in case of success.
        """
        result = yield from self._conn.execute(b'ttl', key, expire)
        return bool(result)

    @asyncio.coroutine
    def inc(self, key):
        """Increment by one the given key.

        :param key: ``bytes``, key to increment.
        :return: ``int`` incremented value
        """
        return (yield from self._conn.execute(b'inc', key))

    @asyncio.coroutine
    def dec(self, key):
        """Decrement by one the given key.

        :param key: ``bytes``, key to decrement.
        :return: ``int`` decremented value in case of success
        """
        return (yield from self._conn.execute(b'dec', key))

    @asyncio.coroutine
    def lock(self, key, expire=0):
        """Prevent the given key from being modified for a given amount
        of seconds.

        :param key: ``bytes``, key to decrement.
        :param expire: ``int``, time in seconds to lock the item.
        :return: ``bool``
        """
        result = yield from self._conn.execute(b'lock', key, expire)
        return bool(result)

    @asyncio.coroutine
    def unlock(self, key):
        """Remove the lock from the given key.

        :param key: ``bytes`` key ot unlock.
        :return: ``bool``, True in case of success.
        """
        result = yield from self._conn.execute(b'unlock', key)
        return bool(result)

    @asyncio.coroutine
    def keys(self, prefix):
        """Return a list of keys matching the given prefix.

        :param prefix: key prefix to use as expression.
        :return: ``list`` of available keys
        """
        result = yield from self._conn.execute(b'keys', prefix)
        keys = [r for i, r in enumerate(result) if i % 2]
        return keys

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

        :param prefix: ``bytes`` The key prefix to use as expression
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
