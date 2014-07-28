import struct
from . import consts
from . import errors


__all__ = ['encode_command', 'Reader']


class Reader(object):
    """XXX"""

    def __init__(self):
        self._buffer = bytearray()
        self._payload = bytearray()
        self._is_header = False
        self._is_payload = False
        self._resp_size = None
        self._gb_encoding = None
        self._code = None

    def feed_data(self, data):
        """
        XXX
        :param data:
        :return:
        """
        if not data:
            return
        self._buffer.extend(data)

    def gets(self):
        """
        XXX
        :return:
        """
        if not self._is_header and len(self._buffer) >= consts.HEADER_SIZE:
            reply = self._buffer[:consts.HEADER_SIZE]
            self._buffer = self._buffer[consts.HEADER_SIZE:]
            unpacked = struct.unpack(b'<HBI', reply)
            self._code, self._gb_encoding, self._resp_size = unpacked
            self._is_header = True

        if (self._is_header and not self._is_payload and
                (len(self._buffer) >= self._resp_size)):
            data = self._buffer[:self._resp_size]
            self._buffer = self._buffer[self._resp_size:]
            self._payload.extend(data)
            self._is_payload = True

        if self._is_header and self._is_payload:
            values = self._parse_replay()
            self._reset()
            return values
        return False

    def _parse_replay(self):
        if self._code == consts.REPL_ERR:
            return errors.GibsonServerError()
        elif self._code == consts.REPL_OK:
            return True
        elif self._code == consts.REPL_ERR_NOT_FOUND:
            return None
        elif self._code == consts.REPL_ERR_NAN:
            return errors.ExpectedANumber()
        elif self._code == consts.REPL_ERR_MEM:
            return errors.MemoryLimitError()
        elif self._code == consts.REPL_ERR_LOCKED:
            return errors.KeyLockedError()
        elif self._code == consts.REPL_VAL:
            return self._parse_value(self._payload, self._gb_encoding)
        elif self._code == consts.REPL_KVAL:
            return self._parse_kv(self._payload)
        else:
            raise errors.ProtocolError()

    def _parse_kv(self, data):
        pairs_num = struct.unpack('I', data[:consts.REPL_SIZE])[0]
        result = []
        offset = consts.REPL_SIZE

        for i in range(pairs_num):
            # unpack key size
            key_size = struct.unpack('I', data[offset: offset + consts.REPL_SIZE])[0]
            offset += consts.REPL_SIZE
            # unpack key
            key = bytes(data[offset: offset + key_size])
            result.append(key)
            offset += key_size
            # unpack value encoding
            value_gb_encodig = struct.unpack('B', data[offset: offset + 1])[0]
            offset += 1
            # unpack value size
            value_size = struct.unpack('I', data[offset: offset + consts.REPL_SIZE])[0]
            offset += consts.REPL_SIZE
            # unpack value
            value = self._parse_value(data[offset: offset + value_size], value_gb_encodig)
            result.append(value)
            offset += value_size
        return result

    def _parse_value(self, data, encoding):
        if encoding == consts.GB_ENC_NUMBER:
            return struct.unpack('q', data)[0]
        elif encoding == consts.GB_ENC_PLAIN:
            return bytes(data)
        else:
            raise errors.ProtocolError()
    def _reset(self):
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
    """
    XXX
    :param command:
    :param args:
    :return:
    """
    _args = []
    for arg in args:

        if type(arg) in _converters:
            barg = _converters[type(arg)](arg)
            _args.append(barg)
        else:
            raise TypeError("Argument {!r} expected to be of bytes,"
                            " str, int or float type".format(arg))

    op_code = consts.command_map[command]
    query = b' '.join(_args)
    fmt = '<IH{}s'.format(len(query))
    data = struct.pack(fmt, consts.OP_CODE_SIZE + len(query), op_code, query)
    return data
