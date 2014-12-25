import asyncio
import unittest

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
        self.gibson_socket = '/tmp/gibson.sock'

    def tearDown(self):
        self.loop.close()
        del self.loop


class GibsonTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.gibson = self.loop.run_until_complete(create_gibson(
            self.gibson_socket, loop=self.loop))

    def tearDown(self):
        self.gibson.close()
        self.loop.run_until_complete(self.gibson.wait_closed())
        del self.gibson
        super().tearDown()
