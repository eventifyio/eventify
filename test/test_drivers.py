import json
import unittest

from datetime import datetime, timedelta

from eventify.service import Service

class TestDrivers(unittest.TestCase):

    def setUp(self):
        pass

    def test_load_driver(self):
        service = Service(config_file='test/config-test.json', handlers=self.test_load_driver)
