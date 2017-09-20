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
        message = event.message
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


    def test_event_name_not_equal(self):
        event_one = Event({
            'name': 'One'
        })

        event_two = Event({
            'name': 'Two'
        })

        is_equal = event_one.__ne__(event_two)
        self.assertTrue(is_equal)

        is_equal = event_one.__eq__(event_two)
        self.assertFalse(is_equal)

    def test_event_name_matches(self):
        event_one = Event({
            'name': 'One',
            'message': 'Test'
        })

        event_two = Event({
            'name': 'One',
            'message': 'Test'
        })

        is_equal = event_one.__eq__(event_two)
        self.assertTrue(is_equal)

        is_equal = event_one.__ne__(event_two)
        self.assertFalse(is_equal)
