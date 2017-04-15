"""
Helper to subscribe to events
"""
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from twisted.internet.defer import inlineCallbacks

from eventify import Eventify


class Subscriber(ApplicationSession, Eventify):
    """
    Handle Subscription Options
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("session ready")

        def oncounter(count):
            """
            topic subscription
            """
            print("event received: {0}", count)
            yield self.subscribe(oncounter, u'com.myapp.oncounter')
            print("subscribed to topic")

    def start(self):
        """
        start subscription
        """
        runner = ApplicationRunner(
            url=self.transport_host, realm=u"realm1")
        runner.run(Subscriber)
