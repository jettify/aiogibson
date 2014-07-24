import asyncio
import unittest
import os

from functools import wraps
from aiogibson.commands import create_gibson


def run_until_complete(fun):
    if not asyncio.iscoroutinefunction(fun):
        fun = asyncio.coroutine(fun)

    @wraps(fun)
    def wrapper(test, *args, **kw):
        loop = test.loop
        ret = loop.run_until_complete(fun(test, *args, **kw))
        return ret
    return wrapper


class BaseTest(unittest.TestCase):
    """Base test case for unittests.
    """

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.gibson_port = int(os.environ.get('GIBSON_PORT') or 10128)
        socket = os.environ.get('REDIS_SOCKET')
        self.gibson_socket = socket or '/tmp/aiogibson.sock'

    def tearDown(self):
        self.loop.close()
        del self.loop


class RedisTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.gibson = self.loop.run_until_complete(create_gibson(
            ('localhost', self.gibson_port), loop=self.loop))

    def tearDown(self):
        self.gibson.close()
        del self.gibson
        super().tearDown()
