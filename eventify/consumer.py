from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

from eventify import Eventify

class ConsumerApp(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        print("session ready")

        def handler(count):
            print("event received: {0}", count)

        try:
            yield self.subscribe(handler, u'mytopic')
            print("subscribed to topic")
        except Exception as e:
            print("could not subscribe to topic: {0}".format(e))


class Consumer(Eventify):

    def start(self):
        """
        Start the event loop
        """
        runner = ApplicationRunner(
            url=self.config['transport_host'],
            realm=u"realm1",
            extra=self.config
        )
        runner.run(ConsumerApp)
