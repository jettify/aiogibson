import unittest
from aiogibson import ProtocolError, ExpectedANumber, MemoryLimitError, \
    KeyLockedError, GibsonError
from aiogibson.parser import Reader, encode_command


class ParserTest(unittest.TestCase):

    def test_not_found(self):
        data = b'\x01\x00\x00\x01\x00\x00\x00\x00'
        parser = Reader()
        parser.feed(data)
        obj = parser.gets()
        self.assertEqual(obj, None)

    def test_val(self):
        data = b'\x06\x00\x00\x03\x00\x00\x00bar'
        parser = Reader()
        parser.feed(data)
        resp = parser.gets()
        self.assertEqual(resp, b'bar')

    def test_kv(self):
        data = b'\x07\x00\x007\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00' \
               b'foo1\x00\x04\x00\x00\x00bar1\x04\x00\x00\x00' \
               b'foo2\x00\x04\x00\x00\x00bar2\x04\x00\x00\x00f' \
               b'oo3\x00\x04\x00\x00\x00bar3'

        parser = Reader()
        parser.feed(data)
        obj = parser.gets()
        expected = [b'foo1', b'bar1', b'foo2', b'bar2', b'foo3', b'bar3']
        self.assertEqual(obj, expected)

    def test_chunked_read(self):
        parser = Reader()
        data = [b'\x06\x00', b'\x00', b'\x03', b'\x00\x00', b'\x00', b'bar']
        parser.feed(b'')
        for i, b in enumerate(data):
            parser.feed(b)
            obj = parser.gets()
            if i == len(data)-1:
                self.assertEqual(obj, b'bar')
            else:
                self.assertEqual(obj, False)

        data2 = [b'\x06\x00', b'\x00', b'\x03', b'\x00\x00', b'\x00', b'zap']
        for i, b in enumerate(data2):
            parser.feed(b)
            obj = parser.gets()
            if i == len(data2) - 1:
                self.assertEqual(obj, b'zap')
            else:
                self.assertEqual(obj, False)

    def test_data_error(self):
        # case where we do not know how to unpack gibson data type
        data = b'\x06\x00\x05\x03\x00\x00\x00bar'
        parser = Reader()
        parser.feed(data)
        with self.assertRaises(ProtocolError):
            parser.gets()

    def test_err_generic(self):
        data = b'\x00\x00\x00\x01\x00\x00\x00\x00'
        parser = Reader()
        parser.feed(data)
        obj = parser.gets()
        self.assertIsInstance(obj, GibsonError)

    def test_err_nan(self):
        data = b'\x02\x00\x00\x01\x00\x00\x00\x00'
        parser = Reader()
        parser.feed(data)
        obj = parser.gets()
        self.assertIsInstance(obj, ExpectedANumber)

    def test_err_mem(self):
        data = b'\x03\x00\x00\x01\x00\x00\x00\x00'
        parser = Reader()
        parser.feed(data)
        obj = parser.gets()
        self.assertIsInstance(obj, MemoryLimitError)

    def test_err_locked(self):
        data = b'\x04\x00\x00\x01\x00\x00\x00\x00'
        parser = Reader()
        parser.feed(data)
        obj = parser.gets()
        self.assertIsInstance(obj, KeyLockedError)

    def test_ok(self):
        data = b'\x05\x00\x00\x01\x00\x00\x00\x00'
        parser = Reader()
        parser.feed(data)
        obj = parser.gets()
        self.assertEqual(obj, True)

    def test_protocol_error(self):
        data = b'\x09\x00\x00\x01\x00\x00\x00\x00'
        parser = Reader()
        parser.feed(data)
        with self.assertRaises(ProtocolError):
            parser.gets()

    def test_gb_encoding(self):
        data = b'\x06\x00\x02\x08\x00\x00\x00M\x00\x00\x00\x00\x00\x00\x00'
        parser = Reader()
        parser.feed(data)
        obj = parser.gets()
        self.assertEqual(obj, 77)

    def test_encode_command_set(self):
        res = encode_command(b'set', 3600, 'foo', 3.14)
        self.assertEqual(res, b'\x0f\x00\x00\x00\x01\x003600 foo 3.14')
        res = encode_command(b'set', 3600, b'foo', bytearray(b'Q'))
        self.assertEqual(res, b'\x0c\x00\x00\x00\x01\x003600 foo Q')

        with self.assertRaises(TypeError):
            encode_command(b'set', b'3600', b'foo', object())
