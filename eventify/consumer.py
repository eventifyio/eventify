from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

from eventify import Eventify

class ConsumerApp(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        print("session ready")
        topics = self.config.extra['config']['subscribed_topics']

        try:
            for topic in topics:
                yield self.subscribe(self.config.extra['callback'], topic)
                print("subscribed to topic: %s" % topic)
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
            extra={'config': self.config, 'callback': self.callback}
        )
        runner.run(ConsumerApp)
