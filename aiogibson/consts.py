"""
Constants for gibson binary protocol

:see: http://gibson-db.in/protocol/
:see: https://github.com/evilsocket/gibson/blob/unstable/src/query.h
"""

# OPERATION CODES
# single
OP_SET = 0x01
OP_TTL = 0x02
OP_GET = 0x03
OP_DEL = 0x04
OP_INC = 0x05
OP_DEC = 0x06
OP_LOCK = 0x07
OP_UNLOCK = 0x08
# multi
OP_MSET = 0x09
OP_MTTL = 0x0A
OP_MGET = 0x0B
OP_MDEL = 0x0C
OP_MINC = 0x0D
OP_MDEC = 0x0E
OP_MLOCK = 0x0F
OP_MUNLOCK = 0x10
# other
OP_COUNT = 0x11
OP_STATS = 0x12
OP_PING = 0x13
OP_META = 0x14
OP_KEYS = 0x15
OP_END = 0xFF


command_map = {
    b'set': OP_SET,
    b'ttl': OP_TTL,
    b'get': OP_GET,
    b'del': OP_DEL,
    b'inc': OP_INC,
    b'dec': OP_DEC,
    b'lock': OP_LOCK,
    b'unlock': OP_UNLOCK,

    b'mset': OP_MSET,
    b'mttl': OP_MTTL,
    b'mget': OP_MGET,
    b'mdel': OP_MDEL,
    b'minc': OP_MINC,
    b'mdec': OP_MDEC,
    b'mlock': OP_MLOCK,
    b'munlock': OP_MUNLOCK,
    b'count': OP_COUNT,

    b'stats': OP_STATS,
    b'ping': OP_PING,
    b'meta': OP_META,
    b'keys': OP_KEYS,
    b'end': OP_END
}


# ENCODING
# Raw string data follows.
GB_ENC_PLAIN = 0x00
# Compressed data, this is a **reserved** value not used for replies.
GB_ENC_LZF = 0x01
# Packed **long** number follows, four bytes for 32bit architectures,
# eight bytes for 64bit.
GB_ENC_NUMBER = 0x02


# **Reply**
REPL_ERR = 0x00
REPL_ERR_NOT_FOUND = 0x01
REPL_ERR_NAN = 0x02
REPL_ERR_MEM = 0x03
REPL_ERR_LOCKED = 0x04
REPL_OK = 0x05
REPL_VAL = 0x06
REPL_KVAL = 0x07


OP_CODE_SIZE = 2
ENCODING_SIZE = 1
REPL_SIZE = 4  # size of block where size of data stored
HEADER_SIZE = OP_CODE_SIZE + ENCODING_SIZE + REPL_SIZE
