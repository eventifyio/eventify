"""
Producer Module
"""
from __future__ import print_function

import json
import requests

from twisted.internet.defer import inlineCallbacks, returnValue

from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import PublishOptions

from eventify import Eventify
from eventify.event import Event

class ProducerApp(ApplicationSession):
    """
    Handle methods for publishing methods to
    transport
    """

    @inlineCallbacks
    def onJoin(self, details):
        """
        Called after connection to crossbar
        """
        self.topic = self.config.extra['publish_topic']['topic']
        self.pub_options = PublishOptions(**self.config.extra['pub_options'])
        event = Event("UiEventProducerStarted")

        # Publish Service Started
        yield self.publish(
            self.topic,
            event,
            options=self.pub_options
        )


class Producer(Eventify):
    """
    Producer class
    """

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

    @inlineCallbacks
    def emit_event(self, event):
        """
        send message over http
        not ideal but for short term
        this is how we will have to proceed
        :param event: eventify.event.Event
        :param asynchronous: Boolean
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

        # convert obj to dict
        if isinstance(event, Event):
            event = dict(
                (key, str(value))
                for (key, value) in event.__dict__.items()
            )

        # build payload
        payload = json.dumps({
            'topic': topic,
            'kwargs': event
        })

        # send message
        response = yield requests.post(http_host, data=payload, headers=headers)
        returnValue(response)
