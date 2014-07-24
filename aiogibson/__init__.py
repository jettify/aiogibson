__version__ = '0.0.1'

from .connection import GibsonConnection, create_connection
from .errors import (GibsonError, ProtocolError, ReplyError,
                     ExpectedANumber, MemoryLimitError, KeyLockedError)

__version__ = '0.1.1'

# make pyflakes happy
(GibsonConnection, create_connection,
    GibsonError, ProtocolError, ReplyError, ExpectedANumber,
    MemoryLimitError, KeyLockedError)
