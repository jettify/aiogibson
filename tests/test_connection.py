import asyncio
from ._testutil import BaseTest, run_until_complete
from aiogibson import create_connection, ProtocolError


class ConnectionTest(BaseTest):

    @run_until_complete
    def test_connect_unixsocket(self):
        conn = yield from create_connection(self.gibson_socket, loop=self.loop)
        res = yield from conn.execute(b'ping')
        self.assertTrue(res)
        self.assertTrue(conn._loop, self.loop)
        conn.close()
        yield from conn.wait_closed()

    @run_until_complete
    def test_global_loop(self):
        asyncio.set_event_loop(self.loop)
        conn = yield from create_connection(self.gibson_socket)
        res = yield from conn.execute(b'ping')
        self.assertTrue(conn._loop, self.loop)
        self.assertTrue(res)
        conn.close()
        yield from conn.wait_closed()

    @run_until_complete
    def test_cancel_future_loop(self):
        conn = yield from create_connection(self.gibson_socket, loop=self.loop)
        res = conn.execute(b'ping')
        res.cancel()
        res = yield from conn.execute(b'ping', encoding='utf-8')
        self.assertTrue(res)
        conn.close()
        yield from conn.wait_closed()

    @run_until_complete
    def test_cancel_futures_in_case_of_close(self):
        conn = yield from create_connection(self.gibson_socket, loop=self.loop)
        res1 = conn.execute(b'ping')
        res2 = conn.execute(b'ping')
        conn.close()
        yield from conn.wait_closed()
        self.assertTrue(res1.cancelled)
        self.assertTrue(res2.cancelled)

    @run_until_complete
    def test_failed_to_decode(self):
        conn = yield from create_connection(self.gibson_socket, loop=self.loop)
        with self.assertRaises(LookupError):
            yield from conn.execute(b'set', 1, b'fo', b'bar',
                                    encoding='utf-10')
        conn.close()
        yield from conn.wait_closed()

    @run_until_complete
    def test_protocol_error(self):
        with self.assertRaises(ProtocolError):
            conn = yield from create_connection(self.gibson_socket,
                                                loop=self.loop)
            conn._parser.feed(b'\x06\x00\x05\x03\x00\x00\x00bar')
            yield from conn.execute(b'ping')

    @run_until_complete
    def test_encoding_property(self):
        conn = yield from create_connection(self.gibson_socket,
                                            encoding='utf-8', loop=self.loop)
        self.assertEqual(conn.encoding, 'utf-8')
        conn.close()
        yield from conn.wait_closed()

    @run_until_complete
    def test_execute(self):
        conn = yield from create_connection(self.gibson_socket, loop=self.loop)
        res = yield from conn.execute(b'ping')
        self.assertTrue(res)

        with self.assertRaises(TypeError):
            yield from conn.execute(None)

        with self.assertRaises(TypeError):
            yield from conn.execute(b'set', None)
        conn.close()
        yield from conn.wait_closed()
