import json
import unittest

from datetime import datetime

from eventify.service import Service

class TestReplay(unittest.TestCase):

    def test_replay_by_timestamp(self):
        service = Service(config_file='test/config-test.json')
        events = service.replay_events(timestamp="2017-01-01")
        self.assertGreater(len(list(events)), 10)

    def test_replay_by_event_id(self):
        service = Service(config_file='test/config-test.json')
        events = service.replay_events(event_id="6bc7a841-3e69-4c3d-963b-e337d12cbeff")
        self.assertGreater(len(list(events)), 2)
