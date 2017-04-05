import os
import pytest
import sys

from eventify import Eventify

class TestEventify:

    def setup_method(self):
        access_key = os.getenv('ACCESS_KEY')
        secret_key = os.getenv('SECRET_KEY')
        region_name = os.getenv('REGION_NAME')
        self.ev = Eventify(access_key, secret_key, 'TestStream', region_name=region_name)

    def test_create_topic(self, capsys):
        response = self.ev.create_topic()
        try:
            status_code = response.get('ResponseMetadata').get('HTTPStatusCode')
            assert status_code == 200
        except AttributeError:
            pass

    def test_delete_topic(self):
        response = self.ev.delete_topic()
        try:
            status_code = response.get('ResponseMetadata').get('HTTPStatusCode')
            assert status_code == 200
        except AttributeError:
            pass
