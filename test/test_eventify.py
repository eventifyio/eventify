import os
import pytest
import sys

from eventify import Eventify

class TestEventify:

    def setup_method(self):
        self.instance = Eventify()

    def test_creating_eventify_instance(self):
        version = self.instance.get_version()
