"""The ``Reader`` class has two methods that are used when parsing replies
from a stream of data. Reader.feed takes a string argument that is appended to
the internal buffer. ``Reader``.gets reads this buffer and returns a reply
when the buffer contains a full reply. If a single call to feed contains
multiple replies, gets should be called multiple times to extract all replies.

>>> reader = aiogibson.Reader()
>>> reader.feed(b'\\x06\\x00\\x05\\x03\\x00\\x00\\x00bar')
>>> reader.gets()
b'bar'

When the buffer does not contain a full reply, gets returns False.
This means extra data is needed and feed should be called again before
calling gets again:

>>> reader.feed(b'\x06\x00\x05')
>>> reader.gets()
False
>>> reader.feed(b'\\x03\\x00\\x00\\x00bar')
>>> reader.gets()
b'bar'

:note: api same as in *hiredis*.


This module has ``encode_command``, packs *gibson* command to binary format
suitable to send over socket to *gibson* server:

>>> encode_command(b'set', 3600, 'foo', 3.14)
b'\\x0f\\x00\\x00\\x00\\x01\\x003600 foo 3.14'
"""
import struct
from . import consts
from . import errors


__all__ = ['encode_command', 'Reader']


class Reader(object):
    """This class is responsible for parsing replies from the stream
    of data that is read from a *Gibson* connection. It does not contain
    functionality to handle I/O
    """

    def __init__(self):
        self._buffer = bytearray()
        self._payload = bytearray()
        self._is_header = False
        self._is_payload = False
        self._resp_size = None
        self._gb_encoding = None
        self._code = None

    def feed(self, data):
        """Put raw chunk of data obtained from connection to buffer.

        :param data: ``bytes``, raw input data.
        """
        if not data:
            return
        self._buffer.extend(data)

    def gets(self):
        """When the buffer does not contain a full reply, gets returns
        False. This means extra data is needed and feed should be called
        again before calling gets again:

        :return: ``False`` there is no full reply or parsed obj.
        """
        if not self._is_header and len(self._buffer) >= consts.HEADER_SIZE:
            reply = self._buffer[:consts.HEADER_SIZE]
            unpacked = struct.unpack(b'<HBI', reply)
            self._code, self._gb_encoding, self._resp_size = unpacked
            self._is_header = True

        if (self._is_header and not self._is_payload and
                (len(self._buffer) >= self._resp_size + consts.HEADER_SIZE)):

            start = consts.HEADER_SIZE
            end = consts.HEADER_SIZE + self._resp_size
            data = self._buffer[start:end]
            self._payload.extend(data)
            self._is_payload = True

        if self._is_header and self._is_payload:
            values = self._parse_replay()
            self._reset()
            return values
        return False

    def _parse_replay(self):
        if self._code == consts.REPL_ERR:
            resp = errors.GibsonServerError()
        elif self._code == consts.REPL_OK:
            resp = True
        elif self._code == consts.REPL_ERR_NOT_FOUND:
            resp = None
        elif self._code == consts.REPL_ERR_NAN:
            resp = errors.ExpectedANumber()
        elif self._code == consts.REPL_ERR_MEM:
            resp = errors.MemoryLimitError()
        elif self._code == consts.REPL_ERR_LOCKED:
            resp = errors.KeyLockedError()
        elif self._code == consts.REPL_VAL:
            resp = self._parse_value(self._payload, self._gb_encoding)
        elif self._code == consts.REPL_KVAL:
            resp = self._parse_kv(self._payload)
        else:
            raise errors.ProtocolError()
        return resp

    def _parse_kv(self, data):
        # parse key/value replay from Gibson server
        pairs_num = struct.unpack('I', data[:consts.REPL_SIZE])[0]
        result = []
        offset = consts.REPL_SIZE

        for i in range(pairs_num):
            # unpack key size
            key_size = \
                struct.unpack('I', data[offset: offset + consts.REPL_SIZE])[0]
            offset += consts.REPL_SIZE
            # unpack key
            key = bytes(data[offset: offset + key_size])
            result.append(key)
            offset += key_size
            # unpack value encoding
            value_gb_encoding = struct.unpack('B', data[offset: offset + 1])[0]
            offset += 1
            # unpack value size
            value_size = \
                struct.unpack('I', data[offset: offset + consts.REPL_SIZE])[0]
            offset += consts.REPL_SIZE
            # unpack value
            value = self._parse_value(data[offset: offset + value_size],
                                      value_gb_encoding)
            result.append(value)
            offset += value_size
        return result

    def _parse_value(self, data, encoding):
        # parse simple value replay from Gibson server.
        # apply gibson encoding if needed
        if encoding == consts.GB_ENC_NUMBER:
            return struct.unpack('q', data)[0]
        elif encoding == consts.GB_ENC_PLAIN:
            return bytes(data)
        else:
            raise errors.ProtocolError()

    def _reset(self):
        # replay parsed, buffer should be prepared for next server
        # reply
        self._buffer = self._buffer[consts.HEADER_SIZE + self._resp_size:]
        self._payload = bytearray()
        self._is_header = False
        self._is_payload = False
        self._resp_size = None
        self._gb_encoding = None
        self._code = None


_converters = {
    bytes: lambda val: val,
    bytearray: lambda val: val,
    str: lambda val: val.encode('utf-8'),
    int: lambda val: str(val).encode('utf-8'),
    float: lambda val: str(val).encode('utf-8'),
    }


def encode_command(command, *args):
    """Pack and encode *gibson* command according to gibson binary protocol

    :see: http://gibson-db.in/protocol/

    :param command: ``bytes``, gibson command (get, set, etc.)
    :param args: required arguments for given command.
    :return: ``bytes`` packed and encoded command.
    """
    _args = []
    for arg in args:
        if type(arg) in _converters:
            _args.append(_converters[type(arg)](arg))
        else:
            raise TypeError("Argument {!r} expected to be of bytes,"
                            " str, int or float type".format(arg))

    op_code = consts.command_map[command]
    query = b' '.join(_args)
    fmt = '<IH{}s'.format(len(query))
    data = struct.pack(fmt, consts.OP_CODE_SIZE + len(query), op_code, query)
    return data
