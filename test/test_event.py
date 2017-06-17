import json
import unittest

from datetime import datetime

from eventify.event import Event


class TestEvent(unittest.TestCase):

    def test_event_string(self):
        event = Event({
            'name': 'TestEvent',
            'message': 'TestBody'
        })
        self.assertIsInstance(event, Event)
        self.assertEqual(event.name, 'TestEvent')
        self.assertEqual(event.message, 'TestBody')


    def test_event_json(self):
        event = Event({
            'name': 'TestEvent',
            'message': {
                'foo': 'bar'
            }
        })
        self.assertIsInstance(event, Event)
        message = json.loads(event.message)
        self.assertIsNotNone(message.get('foo', None))


    def test_event_custom(self):
        event = Event(
            {
                'name': 'TestEvent',
                'message': {
                    'foo': 'bar'
                }
            }, custom_attr='foobar'
        )
        self.assertEqual(event.custom_attr, 'foobar')


    def test_event_no_name(self):
        with self.assertRaises(TypeError):
            event = Event()


    def test_event_no_message(self):
        event = Event({
            'name': 'TestEvent'
        })
        self.assertIsNotNone(event.name)
