import json

from datetime import datetime

from eventify.event import Event

class TestEvent:

    def test_event_string(self):
        event = Event('TestEvent', 'TestBody')
        assert isinstance(event, Event) == True
        assert event.name == 'TestEvent'
        assert event.message == 'TestBody'
        assert isinstance(event.timestamp, datetime)

    def test_event_json(self):
        event = Event('TestEvent', {"foo": "bar"})
        assert isinstance(event, Event) == True
        message = json.loads(event.message)
        assert message.get('foo', None) is not None

    def test_event_custom(self):
        event = Event('TestEvent', {"foo": "bar"}, custom_attr='foobar')
        assert event.custom_attr == 'foobar'

    def test_event_no_name(self):
        try:
            event = Event()
        except TypeError:
            assert True

    def test_event_no_message(self):
        event = Event('TestEvent')
        assert True
