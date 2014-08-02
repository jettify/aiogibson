from ._testutil import GibsonTest, run_until_complete
from aiogibson import errors


class CommandsTest(GibsonTest):
    """Gibson high level commands.

    :see: http://gibson-db.in/commands/
    """

    @run_until_complete
    def test_set(self):
        key, value = b'test:set', b'bar'
        response = yield from self.gibson.set(key, value, expire=3)
        self.assertEqual(response, value)

    @run_until_complete
    def test_get(self):
        key, value = b'test:get', b'bar'
        resp = yield from self.gibson.set(key, value, expire=3)
        self.assertEqual(resp, value)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, value)

    @run_until_complete
    def test_delete(self):
        key, value = b'test:delete', b'zap'
        resp = yield from self.gibson.set(key, value, expire=3)
        self.assertEqual(resp, value)
        resp = yield from self.gibson.delete(key)
        self.assertEqual(resp, True)

        resp = yield from self.gibson.delete(key)
        self.assertEqual(resp, None)

        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, None)

    @run_until_complete
    def test_ttl(self):
        key, value = b'test:ttl', b'zap'
        resp = yield from self.gibson.set(key, value, 3)
        self.assertEqual(resp, value)

        resp = yield from self.gibson.ttl(key, 10)
        self.assertEqual(resp, True)

    @run_until_complete
    def test_inc(self):
        key, value = b'test:inc', 78
        resp = yield from self.gibson.set(key, value, expire=3)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, b'78')
        resp = yield from self.gibson.inc(key)
        self.assertEqual(resp, 79)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, 79)

    @run_until_complete
    def test_dec(self):
        key, value = b'test:dec', 78
        resp = yield from self.gibson.set(key, value, expire=3)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, b'78')
        resp = yield from self.gibson.dec(key)
        self.assertEqual(resp, 77)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, 77)

    @run_until_complete
    def test_lock(self):
        key, value = b'test:lock', b'zap'
        resp = yield from self.gibson.set(key, value, 3)
        self.assertEqual(resp, value)

        resp = yield from self.gibson.lock(key, 10)
        self.assertEqual(resp, True)
        with self.assertRaises(errors.KeyLockedError):
            yield from self.gibson.set(key, value, 3)
        yield from self.gibson.unlock(key)

    def test_unlock(self):
        key, value = b'test:unlock', b'zap'
        resp = yield from self.gibson.set(key, value, 3)
        self.assertEqual(resp, value)

        resp = yield from self.gibson.lock(key, 10)
        self.assertEqual(resp, True)
        with self.assertRaises(errors.KeyLockedError):
            yield from self.gibson.set(key, value, 3)

        resp = yield from self.gibson.unlock(key)
        self.assertEqual(resp, True)
        resp = yield from self.gibson.set(key, 'foo', 3)
        self.assertEqual(resp, b'foo')

    @run_until_complete
    def test_stats(self):
        key, value = b'test:stats', b'zap'
        resp = yield from self.gibson.set(key, value, 3)
        self.assertEqual(resp, value)

        resp = yield from self.gibson.stats()
        test_keys = set([k for i, k in enumerate(resp) if not i % 2])

        expected_keys = set([b'server_version', b'server_build_datetime',
                             b'server_allocator', b'server_arch',
                             b'server_started', b'server_time',
                             b'first_item_seen', b'last_item_seen',
                             b'total_items', b'total_compressed_items',
                             b'total_clients', b'total_cron_done',
                             b'total_connections', b'total_requests',
                             b'memory_available', b'memory_usable',
                             b'memory_used', b'memory_peak',
                             b'memory_fragmentation',
                             b'item_size_avg', b'compr_rate_avg',
                             b'reqs_per_client_avg'])

        self.assertEqual(test_keys, expected_keys)

    @run_until_complete
    def test_keys(self):
        key1, value1 = b'test:keys_1', b'keys:bar'
        key2, value2 = b'test:keys_2', b'keys:zap'
        yield from self.gibson.set(key1, value1, 3)
        yield from self.gibson.set(key2, value2, 3)
        resp = yield from self.gibson.keys(b'test:keys')
        self.assertEqual(resp, [b'0', key1, b'1', key2])

    @run_until_complete
    def test_ping(self):
        result = yield from self.gibson.ping()
        self.assertTrue(result)

    @run_until_complete
    def test_meta(self):
        key, value = b'test:meta_size', b'bar'
        response = yield from self.gibson.set(key, value, expire=10)
        self.assertEqual(response, value)

        res = yield from self.gibson.meta_size(key)
        self.assertEqual(res, 3)

        res = yield from self.gibson.meta_encoding(key)
        self.assertEqual(res, 0)

        res = yield from self.gibson.meta_access(key)
        self.assertTrue(1405555555 < res)

        res = yield from self.gibson.meta_created(key)
        self.assertTrue(1405555555 < res)

        res = yield from self.gibson.meta_ttl(key)
        self.assertEqual(res, 10)

        res = yield from self.gibson.meta_left(key)
        self.assertTrue(10 >= res)

        res = yield from self.gibson.meta_lock(key)
        self.assertEqual(res, 0)

    @run_until_complete
    def test_end(self):
        self.assertTrue(self.gibson.__repr__().startswith("<Gibson"))
        yield from self.gibson.end()
        self.assertTrue(self.gibson.closed)

    @run_until_complete
    def test_mset_mget(self):
        key1, value1 = b'test:mset:1', 10
        key2, value2 = b'test:mset:2', 20
        yield from self.gibson.set(key1, value1, 3)
        yield from self.gibson.set(key2, value2, 130)
        res = yield from self.gibson.mset(b'test:mset', 42)
        self.assertEqual(res, 2)
        res = yield from self.gibson.mget(b'test:mset')
        self.assertEqual(res, [key1, b'42', key2, b'42'])

    @run_until_complete
    def test_mttl(self):
        key1, value1 = b'test:mttl:1', b'mttl:bar'
        key2, value2 = b'test:mttl:2', b'mttl:zap'
        yield from self.gibson.set(key1, value1, 3)
        yield from self.gibson.set(key2, value2, 3)
        resp = yield from self.gibson.mttl(b'test:mttl', 10)
        self.assertEqual(resp, 2)

    @run_until_complete
    def test_minc(self):
        key1, value1 = b'test:minc:1', 10
        key2, value2 = b'test:minc:2', 20
        yield from self.gibson.set(key1, value1, 3)
        yield from self.gibson.set(key2, value2, 3)
        res = yield from self.gibson.minc(b'test:minc')
        self.assertEqual(res, 2)
        res = yield from self.gibson.mget(b'test:minc')
        self.assertEqual(res, [key1, 11, key2, 21])

    @run_until_complete
    def test_mdec(self):
        key1, value1 = b'test:mdec:1', 10
        key2, value2 = b'test:mdec:2', 20
        yield from self.gibson.set(key1, value1, 3)
        yield from self.gibson.set(key2, value2, 3)
        res = yield from self.gibson.mdec(b'test:mdec')
        self.assertEqual(res, 2)
        res = yield from self.gibson.mget(b'test:mdec')
        self.assertEqual(res, [key1, 9, key2, 19])

    @run_until_complete
    def test_mdelete(self):
        key1, value1 = b'test:mdelete:1', 10
        key2, value2 = b'test:mdelete:2', 20
        yield from self.gibson.set(key1, value1, 3)
        yield from self.gibson.set(key2, value2, 3)
        res = yield from self.gibson.mdelete(b'test:mdelete')
        self.assertEqual(res, 2)
        res = yield from self.gibson.mget(b'test:mdelete')
        self.assertEqual(res, None)

    @run_until_complete
    def test_mlock_munlock(self):
        key1, value1 = b'test:mlock:1', 10
        key2, value2 = b'test:mlock:2', 20
        yield from self.gibson.set(key1, value1, 3)
        yield from self.gibson.set(key2, value2, 3)
        yield from self.gibson.mlock(b'test:mlock', expire=3)

        with self.assertRaises(errors.KeyLockedError):
            yield from self.gibson.delete(key1)
        yield from self.gibson.munlock(b'test:mlock')
        res = yield from self.gibson.mdelete(b'test:mlock')
        self.assertEqual(res, 2)

    @run_until_complete
    def test_count(self):
        key1, value1 = b'test:count:1', 10
        key2, value2 = b'test:count:2', 20
        yield from self.gibson.set(key1, value1, 3)
        yield from self.gibson.set(key2, value2, 3)
        res = yield from self.gibson.count(b'test:count')
        self.assertEqual(res, 2)