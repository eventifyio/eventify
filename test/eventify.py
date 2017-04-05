"""
Place Holder Tests
"""
import eventify
import pytest

class TestEventify:

    def setUp(self):
        access_key = os.get('ACCESS_KEY')
        secret_key = os.get('SECRET_KEY')
        region_name = os.get('REGION_NAME')
        self.ev = eventify.Eventify(access_key, secret_key, 'TestStream', region_name=region_name)

    def test_create_topic(self):
        response = self.ev.create_topic()
        print response

    def test_delete_topic(self):
        assert True == True
