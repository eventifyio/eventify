"""
Helper to support publishing events
"""
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks

from eventify import Eventify


class Publisher(ApplicationSession, Eventify):
    """
    Handle Publish Related Options
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("session ready")
        self.publish(u'com.myapp.oncounter', "hi")

    def start(self):
        runner = ApplicationRunner(url=self.transport_host, realm=u"realm1")
        runner.run(Publisher)
