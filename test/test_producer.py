from eventify.event import Event
from eventify.producer import Producer

class TestProducer:

    def test_create_producer(self):
        producer = Producer(config_file='test/config-test.json')

    def test_emit_event(self):
        producer = Producer(config_file='test/config-test.json')
        event = Event('TestEvent', {'foo': 'bar'})
        response = producer.emit_event(event)
        assert response.result.status_code == 200
