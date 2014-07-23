import unittest
from aiogibson.parser import Reader, encode_command


class ParserTest(unittest.TestCase):

    def test_not_found(self):
        data = b'\x01\x00\x00\x01\x00\x00\x00\x00'
        parser = Reader()
        parser.feed_data(data)
        obj = parser.gets()
        self.assertEqual(obj, None)

    def test_val(self):
        data = b'\x06\x00\x00\x03\x00\x00\x00bar'
        parser = Reader()
        parser.feed_data(data)
        obj = parser.gets()
        self.assertEqual(obj, [b'bar'])

    def test_kv(self):
        data = b'\x07\x00\x007\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00' \
               b'foo1\x00\x04\x00\x00\x00bar1\x04\x00\x00\x00' \
               b'foo2\x00\x04\x00\x00\x00bar2\x04\x00\x00\x00f' \
               b'oo3\x00\x04\x00\x00\x00bar3'

        parser = Reader()
        parser.feed_data(data)
        obj = parser.gets()
        expected = [b'foo1', b'bar1', b'foo2', b'bar2', b'foo3', b'bar3']
        self.assertEqual(obj, expected)

    def test_chunked_read(self):
        parser = Reader()
        data = [b'\x06\x00', b'\x00', b'\x03', b'\x00\x00', b'\x00', b'bar']
        for i, b in enumerate(data):
            parser.feed_data(b)
            obj = parser.gets()
            if i == len(data)-1:
                self.assertEqual(obj, [b'bar'])
            else:
                self.assertEqual(obj, False)

        data2 = [b'\x06\x00', b'\x00', b'\x03', b'\x00\x00', b'\x00', b'zap']
        for i, b in enumerate(data2):
            parser.feed_data(b)
            obj = parser.gets()
            if i == len(data2) - 1:
                self.assertEqual(obj, [b'zap'])
            else:
                self.assertEqual(obj, False)

    def test_encode_set(self):
        res = encode_command(b'set', b'3600', b'foo', b'bar')
        self.assertEqual(res, b'\x0e\x00\x00\x00\x01\x003600 foo bar')
