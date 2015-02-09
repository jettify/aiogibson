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

    @asyncio.coroutine
    def wait_closed(self):
        yield from self._conn.wait_closed()

    @property
    def closed(self):
        """True if connection is closed."""
        return self._conn.closed

    def get(self, key):
        """Get the value for a given key.

        :param key: ``bytes``  key to get.
        :return: ``bytes`` if value exists else ``None``
        """
        return self._conn.execute(b'get', key)

    def set(self, key, value, expire=0):
        """Set the value for the given key, with an optional TTL.

        :param key: ``bytes`` key to set.
        :param value: ``bytes`` value to set.
        :param expire: ``int``  optional ttl in seconds
        :raises TypeError: if expire argument is not ``int``
        """
        if not isinstance(expire, int):
            raise TypeError('expire must be int')
        return self._conn.execute(b'set', expire, key, value)

    def delete(self, key):
        """ Delete the given key.

        :param key: ``bytes`` key to delete.
        :return: ``bool`` true in case of success.
        """
        result = self._conn.execute(b'del', key)
        return wait_convert(result, bool)

    def ttl(self, key, expire):
        """Set the TTL of a key.

        :param key: ``bytes``, key to set ttl.
        :param expire: ``int``, TTL in seconds.
        :return: ``bool``, True in case of success.
        :raises TypeError: if expire argument is not ``int``
        """
        if not isinstance(expire, int):
            raise TypeError('expire must be int')
        result = self._conn.execute(b'ttl', key, expire)
        return wait_convert(result, bool)

    def inc(self, key):
        """Increment by one the given key.

        :param key: ``bytes``, key to increment.
        :return: ``int`` incremented value
        """
        return self._conn.execute(b'inc', key)

    def dec(self, key):
        """Decrement by one the given key.

        :param key: ``bytes``, key to decrement.
        :return: ``int`` decremented value in case of success
        """
        return self._conn.execute(b'dec', key)

    def lock(self, key, expire=0):
        """Prevent the given key from being modified for a given amount
        of seconds.

        :param key: ``bytes``, key to decrement.
        :param expire: ``int``, time in seconds to lock the item.
        :return: ``bool``
        :raises TypeError: if expire argument is not ``int``
        """
        if not isinstance(expire, int):
            raise TypeError('expire must be int')
        result = self._conn.execute(b'lock', key, expire)
        return wait_convert(result, bool)

    def unlock(self, key):
        """Remove the lock from the given key.

        :param key: ``bytes`` key ot unlock.
        :return: ``bool``, True in case of success.
        """
        result = self._conn.execute(b'unlock', key)
        return wait_convert(result, bool)

    def keys(self, prefix):
        """Return a list of keys matching the given prefix.

        :param prefix: key prefix to use as expression.
        :return: ``list`` of available keys
        """
        result = self._conn.execute(b'keys', prefix)
        return wait_convert(result, key_pairs)

    def stats(self):
        """Get system stats about the Gibson instance.

        :return: ``list`` of pairs (stat, value).
        """
        return self._conn.execute(b'stats')

    def ping(self):
        """Ping the server instance to refresh client last seen timestamp.

        :return: ``True`` or error.
        """
        return self._conn.execute(b'ping')

    def meta_size(self, key):
        """The size in bytes of the item value.

        :param key: ``bytes``, key of interest.
        :return: ``int``, value size in bytes
        """
        return self._conn.execute(b'meta', key, b'size')

    def meta_encoding(self, key):
        """Gibson encoding for given value.

        :param key: ``bytes``, key of interest.
        :return: ``int``, gibson encoding, 0 - ``bytes``, 2 - ``int``.
        """
        return self._conn.execute(b'meta', key, b'encoding')

    def meta_access(self, key):
        """Timestamp of the last time the item was accessed.

        :param key: ``bytes``, key of interest.
        :return: ``int``, timestamp
        """
        return self._conn.execute(b'meta', key, b'access')

    def meta_created(self, key):
        """Timestamp of item creation.

        :param key: ``bytes``, key of interest.
        :return: ``int``, timestamp
        """
        return self._conn.execute(b'meta', key, b'created')

    def meta_ttl(self, key):
        """Item specified time to live, -1 for infinite TTL.

        :param key: ``bytes``, key of interest.
        :return: ``int``, seconds of TTL.
        """
        return self._conn.execute(b'meta', key,  b'ttl')

    def meta_left(self, key):
        """Number of seconds left for the item to live if a ttl
        was specified, otherwise -1.

        :param key: ``bytes``, key of interest.
        :return: ``int``, Number of seconds left.
        """
        return self._conn.execute(b'meta', key, b'left')

    def meta_lock(self, key):
        """Number of seconds the item is locked, -1 if there's no lock.

        :param key: ``bytes``, key of interest.
        :return: ``int``, number of seconds
        """
        return self._conn.execute(b'meta', key, b'lock')

    def end(self):
        """Disconnects from the client from gibson instance."""
        return self._conn.execute(b'end')

    def mset(self, prefix, value):
        """Set the value for keys verifying the given prefix.

        :param prefix: prefix for keys.
        :return: ``int``, number of modified items, otherwise an error.
        """
        return self._conn.execute(b'mset', prefix, value)

    def mget(self, prefix, limit=None):
        """Get the values for keys with given prefix.

        :param prefix: prefix for keys.
        :param limit: maximum number of returned key/value paris.
        :return: ``list`` of key/value pairs
        :raises TypeError: if limit argument is not ``int``
        """
        if (limit is not None) and (not isinstance(limit, int)):
            raise TypeError('limit must be int')

        if limit is None:
            resp = self._conn.execute(b'mget', prefix)
        else:
            resp = self._conn.execute(b'mget', prefix, limit)
        return resp

    def mttl(self, prefix, expire=0):
        """Set the TTL for keys verifying the given prefix.

        :param prefix: prefix for keys.
        :param expire: ``int``, new expiration time.
        :return: ``int``, number of modified items, otherwise an error.
        :raises TypeError: if expire argument is not ``int``
        """
        if not isinstance(expire, int):
            raise TypeError('expire must be int')
        return self._conn.execute(b'mttl', prefix, expire)

    def minc(self, prefix):
        """Increment by one keys verifying the given prefix.

        :param prefix: prefix for keys.
        :return: ``int``, number of modified items, otherwise an error.
        """
        return self._conn.execute(b'minc', prefix)

    def mdec(self, prefix):
        """Decrement by one keys verifying the given prefix.

        :param prefix: prefix for keys.
        :return: ``int``, number of modified items, otherwise an error.
        """
        return self._conn.execute(b'mdec', prefix)

    def mlock(self, prefix, expire=0):
        """Prevent keys verifying the given prefix from being modified
        for a given amount of seconds.

        :param prefix: ``bytes``, prefix for keys.
        :param expire:``int``, lock period in seconds.
        :return: ``int``, number of modified items, otherwise an error.
        :raises TypeError: if expire argument is not ``int``
        """
        if not isinstance(expire, int):
            raise TypeError('expire must be int')
        return self._conn.execute(b'mlock', prefix, expire)

    def munlock(self, prefix):
        """Remove the lock on keys verifying the given prefix.

        :param prefix: prefix for keys.
        :return: ``int``, number of affected items, otherwise an error.
        """
        return self._conn.execute(b'munlock', prefix)

    def mdelete(self, prefix):
        """Delete keys verifying the given prefix.

        :param prefix: prefix for keys.
        :return: ``int``, number of modified items, otherwise an error.
        """
        return self._conn.execute(b'mdel', prefix)

    def count(self, prefix):
        """Count items for a given prefix.

        :param prefix: ``bytes`` The key prefix to use as expression
        :return: ``int`` number of elements
        """
        return self._conn.execute(b'count', prefix)


@asyncio.coroutine
def create_gibson(address, *, encoding=None, commands_factory=Gibson,
                  loop=None):
    """Create high-level Gibson interface.

    :param address: ``str`` for unix socket path, or ``tuple``
        for (host, port) tcp connection.
    :param encoding: this argument can be used to decode byte-replies to
        strings. By default no decoding is done.
    :param commands_factory:
    :param loop: event loop to use
    :return: high-level Gibson connection ``Gibson``
    """
    conn = yield from create_connection(address, encoding=encoding, loop=loop)
    return commands_factory(conn)


@asyncio.coroutine
def wait_convert(fut, type_):
    result = yield from fut
    return type_(result)


def key_pairs(obj):
    return [r for i, r in enumerate(obj) if i % 2]
