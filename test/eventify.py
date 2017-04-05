import eventify
import os
import pytest

class TestEventify:

    def setup_method(self):
        access_key = os.getenv('ACCESS_KEY')
        secret_key = os.getenv('SECRET_KEY')
        region_name = os.getenv('REGION_NAME')
        self.ev = eventify.Eventify(access_key, secret_key, 'TestStream', region_name=region_name)

    def test_create_topic(self):
        response = self.ev.create_topic()
        print(response)

    def test_delete_topic(self):
        assert True == True
