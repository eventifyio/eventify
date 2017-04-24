"""
Producer Module
"""
import json
import requests

from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import PublishOptions

from eventify import Eventify


class ProducerApp(ApplicationSession):
    """
    Handle methods for publishing methods to
    transport
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("session joined")
        self.topic = self.config.extra['publish_topic']['topic']
        self.pub_options = PublishOptions(**self.config.extra['pub_options'])
        message = json.dumps({
            "event": "UiEventProducerStarted"
        })

        # Publish Service Started
        yield self.publish(
            self.topic,
            message,
            options=self.pub_options
        )


class Producer(Eventify):

    def start(self):
        """
	Run application
	"""

        # Configure application
        runner = ApplicationRunner(
	    url=self.config['transport_host'],
	    realm=u"realm1",
	    extra=self.config
        )

        # Start event loop
        runner.run(
            ProducerApp,
            auto_reconnect=True
        )

    def send_message(self, message):
        """
        send message over http
        not ideal but for short term
        this is how we will have to proceed
        :param message:
        :return: Boolean
        """
        host = self.config['transport_host']
        headers = {
            'Content-Type': 'application/json'
        }

        # split off ws
        url_parts = host.split('/')
        hostname = url_parts[2]
        http_host = 'http://' + hostname + '/publish'

        # get topic
        topic = self.config['publish_topic']['topic']

        # build payload
        payload = json.dumps({
            'topic': topic,
            'kwargs': message
        })

        # send message
        response = requests.post(http_host, data=payload, headers=headers)
        if response.status_code != 200:
            raise ValueError("Invalid payload provided: %s" % payload)
