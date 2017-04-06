import os
import pytest
import sys

from eventify import Eventify

class TestEventify:

    def setup_method(self):
        access_key = os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        region_name = os.getenv('AWS_DEFAULT_REGION')
        self.ev = Eventify(
            driver="kinesis",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            stream_name='TestStream',
            region_name=region_name
        )

    def test_create_topic(self):
        response = self.ev.register_topic()
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
