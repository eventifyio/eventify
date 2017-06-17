import unittest

from eventify.event import Event
from eventify.exceptions import EventifyInitError
from eventify.service import Service


class TestService(unittest.TestCase):

    def test_create_consumer(self):
        with self.assertRaises(EventifyInitError):
            consumer = Service(config_file='test/config-test.json')

    def test_receive_event(self):
        pass
