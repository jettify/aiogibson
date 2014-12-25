"""Pool of connection using context manager protocol:

.. code:: python


    import asyncio
    from aiogibson import create_pool

    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def go():
        pool = yield from create_pool('/tmp/gibson.sock', minsize=5,
                                      maxsize=10, loop=loop)

        with (yield from pool) as gibson:
            yield from gibson.set('foo', 'bar')
            value = yield from gibson.get('foo')
            print(value)

        # or without context manager
        yield from pool.set('foo', 'bar')
        resp = yield from pool.get('foo')
        yield from pool.delete('foo')

        pool.clear()

    loop.run_until_complete(go())
"""
# reference implementation:
# https://github.com/aio-libs/aioredis/blob/master/aioredis/pool.py


import asyncio

from .commands import create_gibson, Gibson

__all__ = ['create_pool', 'GibsonPool']


@asyncio.coroutine
def create_pool(address, *, encoding=None, minsize=10, maxsize=10,
                commands_factory=Gibson, loop=None):
    """Creates Gibson Pool.

    By default it creates pool of commands_factory instances, but it is
    also possible to create pool of plain connections by passing
    ``lambda conn: conn`` as commands_factory.
    All arguments are the same as for create_connection.
    Returns GibsonPool instance.
    """

    pool = GibsonPool(address, encoding=encoding,
                      minsize=minsize, maxsize=maxsize,
                      commands_factory=commands_factory,
                      loop=loop)
    yield from pool._fill_free()
    return pool


class GibsonPool:
    """Gibson connections pool.
    """

    def __init__(self, address, encoding=None,
                 *, minsize, maxsize, commands_factory, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._address = address
        self._minsize = minsize
        self._factory = commands_factory
        self._loop = loop
        self._pool = asyncio.Queue(maxsize, loop=loop)
        self._used = set()
        self._encoding = encoding

    @property
    def minsize(self):
        """Minimum pool size.
        """
        return self._minsize

    @property
    def maxsize(self):
        """Maximum pool size.
        """
        return self._pool.maxsize

    @property
    def size(self):
        """Current pool size.
        """
        return self.freesize + len(self._used)

    @property
    def freesize(self):
        """Current number of free connections.
        """
        return self._pool.qsize()

    @asyncio.coroutine
    def clear(self):
        """Clear pool connections.

        Close and remove all free connections.
        """
        while not self._pool.empty():
            conn = yield from self._pool.get()
            conn.close()
            yield from conn.wait_closed()

    @property
    def encoding(self):
        """Current set codec or None."""
        return self._encoding

    @asyncio.coroutine
    def acquire(self):
        """Acquires a connection from free pool.

        Creates new connection if needed.
        """
        yield from self._fill_free()
        if self.minsize > 0 or not self._pool.empty():
            conn = yield from self._pool.get()
        else:
            conn = yield from self._create_new_connection()
        assert not conn.closed, conn
        assert conn not in self._used, (conn, self._used)
        self._used.add(conn)
        return conn

    def release(self, conn):
        """Returns connection back into pool. Since this method is used
         in ``__exit__()``, this method must not be coroutine.
        """
        assert conn in self._used, "Invalid connection, maybe from other pool"
        self._used.remove(conn)
        if not conn.closed:
            try:
                self._pool.put_nowait(conn)
            except asyncio.QueueFull:
                # consider this connection as old and close it.
                conn.close()

    @asyncio.coroutine
    def _fill_free(self):
        while self.freesize < self.minsize and self.size < self.maxsize:
            conn = yield from self._create_new_connection()
            yield from self._pool.put(conn)

    @asyncio.coroutine
    def _create_new_connection(self):
        conn = yield from create_gibson(self._address,
                                        encoding=self._encoding,
                                        commands_factory=self._factory,
                                        loop=self._loop)
        return conn

    def __enter__(self):
        raise RuntimeError(
            "'yield from' should be used as a context manager expression")

    def __exit__(self, *args):
        pass    # pragma: nocover

    def __iter__(self):
        # this method is needed to allow `yield`ing from pool
        conn = yield from self.acquire()
        return _ConnectionContextManager(self, conn)

    def __getattr__(self, method):
        # we have nice AttributeError here in case *method* is not found in
        # Gibson class (high level interface)
        @asyncio.coroutine
        def caller(*args, **kw):
            with (yield from self) as gibson:
                resp = yield from getattr(gibson, method)(*args, **kw)
            return resp
        return caller


class _ConnectionContextManager:

    __slots__ = ('_pool', '_conn')

    def __init__(self, pool, conn):
        self._pool = pool
        self._conn = conn

    def __enter__(self):
        return self._conn

    def __exit__(self, exc_type, exc_value, tb):
        try:
            self._pool.release(self._conn)
        finally:
            self._pool = None
            self._conn = None
