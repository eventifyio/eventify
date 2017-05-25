"""
Consumer helper
"""
from __future__ import print_function

import logging

from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import SubscribeOptions
from twisted.internet.defer import inlineCallbacks

from eventify import Eventify
from eventify.producer import Producer

logger = logging.getLogger('eventify.consumer')


class ConsumerApp(ApplicationSession):
    """
    Handle subscribing to topics
    """

    @inlineCallbacks
    def onJoin(self, details):
        """
        Upon joining crossbar session
        do things
        """
        logger.debug('connected to crossbar')
        topics = self.config.extra['config']['subscribed_topics']
        subscribe_options = SubscribeOptions(**self.config.extra['config']['sub_options'])

        try:
            for topic in topics:
                yield self.subscribe(
                    self.config.extra['callback'],
                    topic,
                    options=subscribe_options
                )
                logger.debug('subscribed to topic: {0}'.format(topic))
        except Exception as error:
            logger.error('could not subscribe to topic: {0}'.format(error))


class Consumer(Eventify):
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
        runner.run(ConsumerApp)
