import json

from eventify.consumer import Consumer
from eventify.event import Event

class TestConsumer:

    def test_create_consumer(self):
        consumer = Consumer(config_file='test/config-test.json')
        assert True

    def test_receive_event(self):
        pass
