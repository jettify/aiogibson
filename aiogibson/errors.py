__all__ = [
    'GibsonError',
    'ProtocolError',
    'ReplyError',
    'ExpectedANumber',
    'MemoryLimitError',
    'KeyLockedError',
    ]


class GibsonError(Exception):
    """Base exception class for aiogibson exceptions.
    """


class ProtocolError(GibsonError):
    """Raised when protocol error occurs.
    """


class ReplyError(GibsonError):
    """Generic error while executing the query"""


class GibsonServerError(GibsonError):
    """Unknown error on gibson server"""


class ExpectedANumber(GibsonError):
    """Expected a number ( TTL or TIME ) but the specified value
    was invalid."""


class MemoryLimitError(GibsonError):
    """The server reached configuration memory limit and will not accept
    any new value until its freeing routine will be executed."""


class KeyLockedError(GibsonError):
    """The specified key was locked by a OP_LOCK or a OP_MLOCK query."""
