import json
import unittest

from datetime import datetime, timedelta

from eventify.drivers.crossbar import Service as CrossbarService
from eventify.drivers.gmail import Service as GmailService
from eventify.drivers.kafka import Service as KafkaService
from eventify.drivers.zeromq import Service as ZmqService

class TestDrivers(unittest.TestCase):

    def setUp(self):
        pass

    def mock_driver(self):
        pass

    def test_load_driver_crossbar(self):
        service = CrossbarService(config_file='test/config-crossbar.json', handlers=self.mock_driver)
        self.assertIsInstance(service, CrossbarService)

    def test_load_driver_kafka(self):
        service = KafkaService(config_file='test/config-kafka.json', handlers=self.mock_driver)
        self.assertIsInstance(service, KafkaService)

    @unittest.skip("not implemented")
    def test_load_driver_zmq(self):
        service = ZmqService(config_file='test/config-zmq.json', handlers=self.mock_driver)
        self.assertIsInstance(sevrice, ZmqService)

    def test_load_driver_gmail(self):
        service = GmailService(config_file='test/config-gmail.json', handlers=self.mock_driver)
        self.assertIsInstance(service, GmailService)
