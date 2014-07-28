from ._testutil import GibsonTest, run_until_complete
from aiogibson import errors


class CommandsTest(GibsonTest):
    """

    """

    @run_until_complete
    def test_set(self):
        key, value = b'test:set', b'bar'
        response = yield from self.gibson.set(key, value, expire=10)
        self.assertEqual(response, value)

    @run_until_complete
    def test_get(self):
        key, value = b'test:get', b'bar'
        resp = yield from self.gibson.set(key, value, expire=10)
        self.assertEqual(resp, value)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, value)

    @run_until_complete
    def test_delete(self):
        key, value = b'test:delete', b'zap'
        resp = yield from self.gibson.set(key, value, expire=10)
        self.assertEqual(resp, value)
        resp = yield from self.gibson.delete(key)
        self.assertEqual(resp, True)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, None)

    @run_until_complete
    def test_ttl(self):
        key, value = b'test:ttl', b'zap'
        resp = yield from self.gibson.set(key, value)
        self.assertEqual(resp, value)

        resp = yield from self.gibson.ttl(key, 10)
        self.assertEqual(resp, True)

    @run_until_complete
    def test_inc(self):
        key, value = b'test:inc', 78
        resp = yield from self.gibson.set(key, value, expire=10)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, b'78')
        resp = yield from self.gibson.inc(key)
        self.assertEqual(resp, 79)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, 79)

    @run_until_complete
    def test_dec(self):
        key, value = b'test:dec', 78
        resp = yield from self.gibson.set(key, value, expire=10)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, b'78')
        resp = yield from self.gibson.dec(key)
        self.assertEqual(resp, 77)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, 77)

    @run_until_complete
    def test_lock(self):
        key, value = b'test:lock', b'zap'
        resp = yield from self.gibson.set(key, value)
        self.assertEqual(resp, value)

        resp = yield from self.gibson.lock(key, 10)
        self.assertEqual(resp, True)
        with self.assertRaises(errors.KeyLockedError):
            yield from self.gibson.set(key, value)
        yield from self.gibson.unlock(key)


    def test_unlock(self):
        key, value = b'test:unlock', b'zap'
        resp = yield from self.gibson.set(key, value)
        self.assertEqual(resp, value)

        resp = yield from self.gibson.lock(key, 10)
        self.assertEqual(resp, True)
        with self.assertRaises(errors.KeyLockedError):
            yield from self.gibson.set(key, value)

        resp = yield from self.gibson.unlock(key)
        self.assertEqual(resp, True)
        res = yield from self.gibson.set(key, 'foo')
        self.assertEqual(resp, b'foo')

    @run_until_complete
    def test_stats(self):
        key, value = b'test:ttl', b'zap'
        resp = yield from self.gibson.set(key, value)
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
        yield from self.gibson.set(key1, value1, 100)
        yield from self.gibson.set(key2, value2, 100)
        resp = yield from self.gibson.keys(b'test:keys')
        self.assertEqual(resp, [b'0', key1, b'1', key2])