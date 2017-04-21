"""
Producer Module
"""
import json

from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import PublishOptions

from eventify import Eventify

class ProducerApp(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        print('session joined')
        topic = self.config.extra['publish_topic']['topic']
        pub_options = PublishOptions(**self.config.extra['pub_options'])
        message = json.dumps({
            "event": "UiEventProducerStarted"
        })
        yield self.publish(
            topic,
            message,
            options=pub_options
        )

class Producer(Eventify):

    def start(self):
        """
	Start the event loop
	"""
        runner = ApplicationRunner(
	    url=self.config['transport_host'],
	    realm=u"realm1",
	    extra=self.config
        )
        runner.run(ProducerApp)
