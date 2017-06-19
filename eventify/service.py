"""
Service Module
"""
from __future__ import print_function

import logging
import json

import requests

from autobahn.wamp.exception import ProtocolError
from autobahn.twisted.wamp import Session, ApplicationRunner
from autobahn.wamp.types import SubscribeOptions, PublishOptions
from twisted.internet.defer import inlineCallbacks, returnValue

from eventify import Eventify
from eventify.event import Event
from eventify.persist import persist_event


logger = logging.getLogger('eventify.service')


class Component(Session):
    """
    Handle subscribing to topics
    """

    def publish(self, topic, event, options=None):
        """
        Override publish method to support
        event store pattern
        """
        if self.config.extra['config']['pub_options']['retain']:
            try:
                persist_event(topic, event)
            except SystemError as error:
                logger.error(error)
                return

        super().publish(
            topic,
            event.as_json(),
            options=self.publish_options
        )


    def onConnect(self):
        """
        Configure the component
        """

        # subscription setup
        self.subcribed_topics = self.config.extra['config']['subscribed_topics']
        self.subscribe_options = SubscribeOptions(**self.config.extra['config']['sub_options'])

        # publishing setup
        self.publish_topic = self.config.extra['config']['publish_topic']['topic']
        self.publish_options = PublishOptions(**self.config.extra['config']['pub_options'])

        # join topic
        self.callback = self.config.extra['callback']
        self.join(self.config.realm)


    @inlineCallbacks
    def emit_event(self, event):
        """
        Publish an event back to crossbar
        :param event: Event object
        """
        yield self.publish(
            self.publish_topic,
            event,
            options=self.publish_options
        )


    @inlineCallbacks
    def onJoin(self, details):
        logger.debug("session attached: %s" % details)

        def transport_event(*args, **kwargs):
            """
            Send event to application code
            """
            try:
                event = args[0]['kwargs']
            except IndexError:
                event = kwargs
            self.callback(event, session=self)

        for topic in self.subcribed_topics:
            pub = yield self.subscribe(
                transport_event,
                topic,
                options=self.subscribe_options
            )

            if self.config.extra['config']['replay_events']:
                events = yield self.call(u"wamp.subscription.get_events", pub.id, 1000)
                for event in reversed(events):
                    transport_event(event)


class Service(Eventify):
    """
    Start consumer
    """

    def start(self):
        """
        Start the event loop
        """
        logger.debug('starting event loop')
        runner = ApplicationRunner(
            url=self.config['transport_host'],
            realm=u'realm1',
            extra={'config': self.config, 'callback': self.callback}
        )
        runner.run(Component, auto_reconnect=True)
