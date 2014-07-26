from ._testutil import BaseTest, run_until_complete
from aiogibson import create_connection


class ConnectionTest(BaseTest):

    @run_until_complete
    def test_connect_unixsocket(self):
        conn = yield from create_connection(self.gibson_socket, loop=self.loop)
        res = yield from conn.execute(b'ping')
        self.assertTrue(res)
