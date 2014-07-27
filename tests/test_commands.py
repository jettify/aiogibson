from ._testutil import GibsonTest, run_until_complete


class CommandsTest(GibsonTest):

    @run_until_complete
    def test_set(self):
        key, value = b'test:set', b'bar'
        response = yield from self.gibson.set(key, value, ttl=10)
        self.assertEqual(response, value)

    @run_until_complete
    def test_get(self):
        key, value = b'test:get', b'bar'
        resp = yield from self.gibson.set(key, value, ttl=10)
        self.assertEqual(resp, value)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, value)

    @run_until_complete
    def test_delete(self):
        key, value = b'test:delete', b'zap'
        resp = yield from self.gibson.set(key, value, ttl=10)
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
        resp = yield from self.gibson.set(key, value, ttl=10)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, b'78')
        resp = yield from self.gibson.inc(key)
        self.assertEqual(resp, 79)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, 79)

    @run_until_complete
    def test_dec(self):
        key, value = b'test:inc', 78
        resp = yield from self.gibson.set(key, value, ttl=10)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, b'78')
        resp = yield from self.gibson.dec(key)
        self.assertEqual(resp, 77)
        resp = yield from self.gibson.get(key)
        self.assertEqual(resp, 77)
