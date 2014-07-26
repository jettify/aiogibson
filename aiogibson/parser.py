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
        self._encoding = None
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
            unpacked = struct.unpack(b'<HcI', reply)
            self._code, self._encoding, self._resp_size = unpacked
            self._is_header = True

        if (self._is_header and not self._is_payload and
                (len(self._buffer) >= self._resp_size)):
            data = self._buffer[:self._resp_size]
            self._buffer = self._buffer[self._resp_size:]
            self._payload.extend(data)
            self._is_payload = True

        if self._is_header and self._is_payload:
            values = self._parse_replay(self._code, self._payload)
            self._reset()
            return values
        return False

    def _parse_replay(self, code, data):
        if code == consts.REPL_ERR:
            return errors.GibsonServerError()
        elif code == consts.REPL_OK:
            return True
        elif code == consts.REPL_ERR_NOT_FOUND:
            return None
        elif code == consts.REPL_ERR_NAN:
            return errors.ExpectedANumber()
        elif code == consts.REPL_ERR_MEM:
            return errors.MemoryLimitError()
        elif code == consts.REPL_ERR_LOCKED:
            return errors.KeyLockedError()
        elif code == consts.REPL_VAL:
            return self._parse_values(data)
        elif code == consts.REPL_KVAL:
            return self._parse_kv(data)
        else:
            raise errors.ProtocolError()

    def _parse_kv(self, data):
        entities_num = struct.unpack('I', data[:consts.REPL_SIZE])[0]
        entities = [None]*entities_num*2
        entities = self._parse_entity(entities, 0, data[consts.REPL_SIZE:])
        return entities

    def _parse_entity(self, result, cursor, data, encoding=False):
        if not data:
            return result
        offset = int(encoding)

        entity_size = struct.unpack('I',
                                    data[offset:consts.REPL_SIZE + offset])[0]
        _start = consts.REPL_SIZE + offset
        _end = consts.REPL_SIZE + offset + entity_size
        entity = data[_start: _end]
        _data = data[consts.REPL_SIZE + offset + entity_size:]
        result[cursor] = bytes(entity)
        result = self._parse_entity(result, cursor+1, _data, not encoding)
        return result

    def _parse_values(self, data):
        return [bytes(v) for v in data.split()]

    def _reset(self):
        self._payload = bytearray()
        self._is_header = False
        self._is_payload = False
        self._resp_size = None
        self._encoding = None
        self._code = None


def encode_command(command, *args):
    """
    XXX
    :param command:
    :param args:
    :return:
    """
    op_code = consts.command_map[command]
    query = b' '.join(args)
    fmt = '<IH{}s'.format(len(query))
    data = struct.pack(fmt, consts.OP_CODE_SIZE + len(query), op_code, query)
    return data
