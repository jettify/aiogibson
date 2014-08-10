"""
Borrowed from aioredis.

:see: https://github.com/aio-libs/aioredis/blob/master/aioredis/connection.py
"""

import asyncio

from .errors import GibsonError, ProtocolError
from .parser import Reader, encode_command


__all__ = ['create_connection', 'GibsonConnection']

MAX_CHUNK_SIZE = 65536
_NOTSET = object()


@asyncio.coroutine
def create_connection(address, *, encoding=None, loop=None):
    """Creates GibsonConnection connection.
    Opens connection to Gibson server specified by address argument.

    :param address: ``str`` for unix socket path, or ``tuple``
        for (host, port) tcp connection.
    :param encoding: this argument can be used to decode byte-replies to
    strings. By default no decoding is done.
    """
    assert isinstance(address, (tuple, list, str)), "tuple or str expected"

    if isinstance(address, (list, tuple)):
        host, port = address
        reader, writer = yield from asyncio.open_connection(
            host, port, loop=loop)
    else:
        reader, writer = yield from asyncio.open_unix_connection(
            address, loop=loop)
    conn = GibsonConnection(reader, writer, address=address,
                            encoding=encoding, loop=loop)
    return conn


class GibsonConnection:
    """Gibson connection."""

    def __init__(self, reader, writer, address, *, encoding=None, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._reader = reader
        self._writer = writer
        self._loop = loop
        self._waiters = asyncio.Queue(loop=self._loop)
        self._parser = Reader()
        self._reader_task = asyncio.Task(self._read_data(), loop=self._loop)
        self._closing = False
        self._closed = False
        self._address = address
        self._encoding = encoding

    def __repr__(self):
        return '<GibsonConnection {}>'.format(self._address)

    @asyncio.coroutine
    def _read_data(self):
        """Responses reader task."""
        while not self._reader.at_eof():
            data = yield from self._reader.read(MAX_CHUNK_SIZE)
            self._parser.feed_data(data)
            while True:
                try:
                    obj = self._parser.gets()
                except ProtocolError as exc:
                    # ProtocolError is fatal
                    # so connection must be closed
                    self._closing = True
                    self._loop.call_soon(self._do_close, exc)
                    return
                else:
                    if obj is False:
                        break
                    waiter = yield from self._waiters.get()
                    if isinstance(obj, GibsonError):
                        waiter.set_exception(obj)
                    else:
                        waiter.set_result(obj)
        self._closing = True
        self._loop.call_soon(self._do_close, None)

    @asyncio.coroutine
    def execute(self, command, *args, encoding=_NOTSET):
        assert self._reader and not self._reader.at_eof(), (
            "Connection closed or corrupted")
        command = command.strip()
        data = encode_command(command, *args)
        self._writer.write(data)
        yield from self._writer.drain()
        fut = asyncio.Future(loop=self._loop)
        yield from self._waiters.put(fut)
        result = yield from fut
        if encoding is _NOTSET:
            encoding = self._encoding
        if encoding is not None and isinstance(result, bytes):
            return result.decode(encoding)
        return result

    def close(self):
        """Close connection."""
        self._do_close(None)

    def _do_close(self, exc):
        if self._closed:
            return
        self._closed = True
        self._closing = False
        self._writer.transport.close()
        self._reader_task.cancel()
        self._reader_task = None
        self._writer = None
        self._reader = None
        while self._waiters.qsize():
            waiter = self._waiters.get_nowait()
            if exc is None:
                waiter.cancel()
            else:
                waiter.set_exception(exc)

    @property
    def closed(self):
        """True if connection is closed."""
        closed = self._closing or self._closed
        if not closed and self._reader and self._reader.at_eof():
            self._closing = closed = True
            self._loop.call_soon(self._do_close, None)
        return closed

    @property
    def encoding(self):
        """Current set codec or None."""
        return self._encoding
