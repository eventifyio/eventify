import json
import unittest

from eventify.event import Event
from eventify.tracking import track_event, get_last_event
from eventify.tracking.constants import EventState

class TestTracking(unittest.TestCase):

    @unittest.skip('redis not available via travisci')
    def test_get_last_event(self):
        service_name = 'example'
        get_last_event(service_name)
