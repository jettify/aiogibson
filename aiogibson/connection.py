"""Low level connection with raw interface."""
# Borrowed from aioredis.
# :see: https://github.com/aio-libs/aioredis/blob/master/aioredis/connection.py

import asyncio
from collections import deque

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
        self._waiters = deque()
        self._parser = Reader()
        self._reader_task = asyncio.Task(self._read_data(), loop=self._loop)
        self._closing = False
        self._closed = False
        self._close_waiter = asyncio.Future(loop=self._loop)
        self._reader_task.add_done_callback(self._close_waiter.set_result)
        self._address = address
        self._encoding = encoding

    def __repr__(self):
        return '<GibsonConnection {}>'.format(self._address)

    @asyncio.coroutine
    def _read_data(self):
        """Responses reader task."""
        while not self._reader.at_eof() and not self._closed:
            data = yield from self._reader.read(MAX_CHUNK_SIZE)
            self._parser.feed(data)
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
                    fut, encoding = self._waiters.popleft()
                    if fut.done():  # waiter possibly
                        assert fut.cancelled(), (
                            "waiting future is in wrong state", fut, obj)
                        continue
                    if isinstance(obj, GibsonError):
                        fut.set_exception(obj)
                    else:
                        if encoding is not None and isinstance(obj, bytes):
                            try:
                                obj = obj.decode(encoding)
                            except Exception as exc:
                                fut.set_exception(exc)
                                continue
                        fut.set_result(obj)

        self._closing = True
        self._loop.call_soon(self._do_close, None)

    def execute(self, command, *args, encoding=_NOTSET):
        """Executes raw gibson command.

        :param command: ``str`` or ``bytes`` gibson command.
        :param args: tuple of arguments required for gibson command.
        :param encoding: ``str`` default encoding for unpacked data.

        :raises TypeError: if any of args can not be encoded as bytes.
        :raises ProtocolError: when response can not be decoded meaning
            connection is broken.
        """
        assert self._reader and not self._reader.at_eof(), (
            "Connection closed or corrupted")
        if command is None:
            raise TypeError("command must not be None")
        if None in set(args):
            raise TypeError("args must not contain None")
        command = command.strip()
        data = encode_command(command, *args)
        if encoding is _NOTSET:
            encoding = self._encoding
        fut = asyncio.Future(loop=self._loop)
        self._waiters.append((fut, encoding))
        self._writer.write(data)
        return fut

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
        while self._waiters:
            (waiter, _) = self._waiters.pop()
            if exc is None:
                waiter.cancel()
            else:
                waiter.set_exception(exc)

    @asyncio.coroutine
    def wait_closed(self):
        yield from self._close_waiter

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
