"""
Copied from:
:see: https://github.com/aio-libs/aioredis/blob/master/tests/pool_test.py
"""
import asyncio

from ._testutil import BaseTest, run_until_complete
from aiogibson import create_pool, create_gibson, GibsonPool


class PoolTest(BaseTest):

    def _assert_defaults(self, pool):
        self.assertIsInstance(pool, GibsonPool)
        self.assertEqual(pool.minsize, 10)
        self.assertEqual(pool.maxsize, 10)
        self.assertEqual(pool.size, 10)
        self.assertEqual(pool.freesize, 10)

    def test_connect(self):
        pool = self.loop.run_until_complete(create_pool(
            self.gibson_socket, loop=self.loop))
        self._assert_defaults(pool)

    def test_global_loop(self):
        asyncio.set_event_loop(self.loop)

        pool = self.loop.run_until_complete(create_pool(
            self.gibson_socket))
        self._assert_defaults(pool)

    @run_until_complete
    def test_clear(self):
        pool = yield from create_pool(
            self.gibson_socket, loop=self.loop)
        self._assert_defaults(pool)

        yield from pool.clear()
        self.assertEqual(pool.freesize, 0)

    @run_until_complete
    def test_no_yield_from(self):
        pool = yield from create_pool(
            self.gibson_socket, loop=self.loop)

        with self.assertRaises(RuntimeError):
            with pool:
                pass

    @run_until_complete
    def test_simple_command(self):
        pool = yield from create_pool(
            self.gibson_socket,
            minsize=10, loop=self.loop)

        with (yield from pool) as conn:
            msg = yield from conn.ping()
            self.assertTrue(msg)
            self.assertEqual(pool.size, 10)
            self.assertEqual(pool.freesize, 9)
        self.assertEqual(pool.size, 10)
        self.assertEqual(pool.freesize, 10)

    @run_until_complete
    def test_simple_without_context_manager(self):
        pool = yield from create_pool(
            self.gibson_socket,
            minsize=10, loop=self.loop)

        msg = yield from pool.ping()
        self.assertTrue(msg)
        yield from pool.set(b'foo', b'bar', 7)
        result = yield from pool.get(b'foo')
        self.assertEqual(result, b'bar')
        resp = yield from pool.delete(b'foo')
        self.assertTrue(resp)

        with self.assertRaises(AttributeError):
            yield from pool.zadd(b'foo')

        self.assertEqual(pool.size, 10)
        self.assertEqual(pool.freesize, 10)

    @run_until_complete
    def test_create_new(self):
        pool = yield from create_pool(
            self.gibson_socket,
            minsize=1, loop=self.loop)
        self.assertEqual(pool.size, 1)
        self.assertEqual(pool.freesize, 1)

        with (yield from pool):
            self.assertEqual(pool.size, 1)
            self.assertEqual(pool.freesize, 0)

            with (yield from pool):
                self.assertEqual(pool.size, 2)
                self.assertEqual(pool.freesize, 0)

        self.assertEqual(pool.size, 2)
        self.assertEqual(pool.freesize, 2)

    @run_until_complete
    def test_create_constraints(self):
        pool = yield from create_pool(
            self.gibson_socket,
            minsize=1, maxsize=1, loop=self.loop)
        self.assertEqual(pool.size, 1)
        self.assertEqual(pool.freesize, 1)

        with (yield from pool):
            self.assertEqual(pool.size, 1)
            self.assertEqual(pool.freesize, 0)

            with self.assertRaises(asyncio.TimeoutError):
                yield from asyncio.wait_for(pool.acquire(),
                                            timeout=0.2,
                                            loop=self.loop)

    @run_until_complete
    def test_create_no_minsize(self):
        pool = yield from create_pool(
            self.gibson_socket,
            minsize=0, maxsize=1, loop=self.loop)
        self.assertEqual(pool.size, 0)
        self.assertEqual(pool.freesize, 0)

        with (yield from pool):
            self.assertEqual(pool.size, 1)
            self.assertEqual(pool.freesize, 0)

            with (yield from pool):
                self.assertEqual(pool.size, 2)
                self.assertEqual(pool.freesize, 0)
        self.assertEqual(pool.size, 1)
        self.assertEqual(pool.freesize, 1)

    @run_until_complete
    def test_release_closed(self):
        pool = yield from create_pool(
            self.gibson_socket,
            minsize=1, loop=self.loop)
        self.assertEqual(pool.size, 1)
        self.assertEqual(pool.freesize, 1)

        with (yield from pool) as gibson:
            gibson.close()
        self.assertEqual(pool.size, 0)
        self.assertEqual(pool.freesize, 0)

    @run_until_complete
    def test_release_bad_connection(self):
        pool = yield from create_pool(
            self.gibson_socket,
            loop=self.loop)
        yield from pool.acquire()
        other_conn = yield from create_gibson(
            self.gibson_socket,
            loop=self.loop)
        with self.assertRaises(AssertionError):
            pool.release(other_conn)

    @run_until_complete
    def test_response_decoding(self):
        pool = yield from create_pool(
            self.gibson_socket,
            encoding='utf-8', loop=self.loop)

        self.assertEqual(pool.encoding, 'utf-8')
        with (yield from pool) as gibson:
            yield from gibson.set('key', 'value')
        with (yield from pool) as gibson:
            res = yield from gibson.get('key')
            self.assertEqual(res, 'value')
