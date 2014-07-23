import struct
from . import consts
from . import errors


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
            return
        elif code == consts.REPL_OK:
            return True
        elif code == consts.REPL_ERR_NOT_FOUND:
            return None
        elif code == consts.REPL_ERR_NAN:
            return errors.ExpectedANumber()
        elif code == consts.REPL_ERR_MEM:
            return errors.ExpectedANumber()
        elif code == consts.REPL_ERR_LOCKED:
            return errors.KeyLockedError()
        elif code == consts.REPL_VAL:
            return self._parse_values(data)
        elif code == consts.REPL_KVAL:
            return self._parse_kv(data)
        else:
            raise errors.GibsonError()

    def _parse_kv(self, data):
        entities_num = struct.unpack('I', data[:4])[0]
        entities = self._parse_entity(data[4:])
        if not entities_num*2 == len(entities):
            raise errors.ProtocolError
        return entities

    def _parse_entity(self, data, encoding=False):
        if not data:
            return []
        offset = int(encoding)
        entity_size = struct.unpack('I', data[offset:4 + offset])[0]
        entity = data[4 + offset: 4 + offset + entity_size]
        _data = data[4 + offset + entity_size:]
        tail = self._parse_entity(_data, not encoding)
        return [bytes(entity)] + tail

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
