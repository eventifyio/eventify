import os
import pytest
import sys

from eventify import Eventify

class TestEventify:

    def setup_method(self):
        self.instance = Eventify()

    def test_placeholder(self):
        assert True == True
