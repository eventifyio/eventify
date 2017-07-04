import json
import unittest

from datetime import datetime, timedelta

from eventify.drivers.crossbar import Component

class TestReplay(unittest.TestCase):

    def setUp(self):
        self.component = Component()
        self.component.config.extra = {}
        self.component.config.extra['config'] = {
            'name': 'test/agent',
            'replay_events': True,
            'replay_type': 'event_store',
            'publish_topic': {
                'topic': 'example'
            },
            'subscribed_topics': [
                'example'
            ],
            'sub_options': {
                'get_retained': False
            },
            'pub_options': {
                'acknowledge': True,
                'retain': True
            }
        }
        self.component.config.extra['callback'] = self.test_replay_by_event_id
        try:
            self.component.onConnect()
        except AttributeError:
            pass


    @unittest.skip('replay callback errors')
    def test_replay_by_timestamp(self):
        now = datetime.utcnow()
        last_week = now - timedelta(days=7)
        events = self.component.replay_events(timestamp=last_week)
        self.assertGreater(len(list(events)), 1)


    @unittest.skip('replay callback errors')
    def test_replay_by_event_id(self, **kwargs):
        events = self.component.replay_events(event_id="6bc7a841-3e69-4c3d-963b-e337d12cbeff")
        self.assertGreater(len(list(events)), 1)
