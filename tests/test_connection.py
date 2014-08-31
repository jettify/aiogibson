from ._testutil import BaseTest, run_until_complete
from aiogibson import create_connection


class ConnectionTest(BaseTest):

    @run_until_complete
    def test_connect_unixsocket(self):
        conn = yield from create_connection(self.gibson_socket, loop=self.loop)
        res = yield from conn.execute(b'ping')
        self.assertTrue(res)

    @run_until_complete
    def test_encoding_property(self):
        conn = yield from create_connection(self.gibson_socket,
                                            encoding='utf-8', loop=self.loop)
        self.assertEqual(conn.encoding, 'utf-8')

    @run_until_complete
    def test_execute(self):
        conn = yield from create_connection(self.gibson_socket, loop=self.loop)
        res = yield from conn.execute(b'ping')
        self.assertTrue(res)

        with self.assertRaises(TypeError):
            yield from conn.execute(None)

        with self.assertRaises(TypeError):
            yield from conn.execute(b'set', None)
