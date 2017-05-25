"""
Producer Module
"""
from __future__ import print_function

import json
import logging

import requests
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import PublishOptions
from twisted.internet.defer import inlineCallbacks, returnValue

from eventify import Eventify
from eventify.event import Event

logger = logging.getLogger('eventify.producer')


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
        logger.debug('connected to crossbar')
        self.topic = self.config.extra['publish_topic']['topic']
        self.pub_options = PublishOptions(**self.config.extra['pub_options'])
        logger.debug(details)


class Producer(Eventify):
    """
    Producer class
    """

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
        logger.warning('publishing over http is deprecated; see documentation')
        logger.debug('emitting event: {0}'.format(event.name))

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
        logger.debug('event {0} successfully emitted'.format(event['name']))

        returnValue(response)
