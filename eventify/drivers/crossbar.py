"""
Crossbar Driver Module
"""
from __future__ import print_function

import logging
import sys
import traceback

import asyncpg

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import SubscribeOptions, PublishOptions

from eventify.persist import persist_event
from eventify.persist.constants import EVENT_DB_HOST, EVENT_DB_USER, EVENT_DB_PASS, \
    EVENT_DB_NAME
from eventify import Eventify

logger = logging.getLogger('eventify.drivers.crossbar')


class Component(ApplicationSession):
    """
    Handle subscribing to topics
    """

    async def onConnect(self):
        """
        Configure the component
        """

        # subscription setup
        self.subscribed_topics = self.config.extra['config']['subscribed_topics']
        self.subscribe_options = SubscribeOptions(**self.config.extra['config']['sub_options'])
        self.replay_events = self.config.extra['config']['replay_events']

        # publishing setup
        self.publish_topic = self.config.extra['config']['publish_topic']['topic']
        self.publish_options = PublishOptions(**self.config.extra['config']['pub_options'])

        # setup callback
        self.handlers = self.config.extra['handlers']

        # put name on session
        self.name = self.config.extra['config']['name']

        # setup db pool
        self.pool = await asyncpg.create_pool(
            user=EVENT_DB_USER,
            password=EVENT_DB_PASS,
            host=EVENT_DB_HOST,
            database=EVENT_DB_NAME
        )

        # Check for replay option
        # if self.replay_events:
        #   await replay_events(self)

        # join topic
        print("connected")
        self.join(self.config.realm)

    async def emit_event(self, event):
        """
        Publish an event back to crossbar
        :param event: Event object
        """
        logger.debug("publishing event on %s", self.publish_topic)
        if self.config.extra['config']['pub_options']['retain']:
            try:
                logger.debug("persisting event")
                await persist_event(
                    self.publish_topic,
                    event,
                    self.pool
                )
                logger.debug("event persisted")
            except SystemError as error:
                logger.error(error)
                return

        await self.publish(
            self.publish_topic,
            event.__dict__,
            options=self.publish_options
        )

    async def onJoin(self, details):
        logger.debug("joined websocket realm: %s", details)

        for handler in self.handlers:
            handler.set_session(self)
            if hasattr(handler, 'init'):
                await handler.init()
            if hasattr(handler, 'on_event'):
                # Subscribe to all of the topics in configuration
                for topic in self.subscribed_topics:
                    logger.debug("subscribing to topic %s", topic)
                    await self.subscribe(
                        handler.on_event,
                        handler.subscribe_topic,
                    )
                    logger.debug("subscribed to topic: %s", topic)

            if hasattr(handler, 'worker'):
                # or just await handler.worker()
                while True:
                    try:
                        await handler.worker()
                    except Exception:
                        print("Operation failed. Go to next item...")
                        traceback.print_exc(file=sys.stdout)
                        continue

    async def show_sessions(self):
        """
        Returns an object with a lists of the session IDs
        for all sessions currently attached to the realm

        http://crossbar.io/docs/Session-Metaevents-and-Procedures/
        """
        res = await self.call("wamp.session.list")
        for session_id in res:
            session = await self.call("wamp.session.get", session_id)
            print(session)

    async def total_sessions(self):
        """
        Returns the number of sessions currently attached to the realm.

        http://crossbar.io/docs/Session-Metaevents-and-Procedures/
        """
        res = await self.call("wamp.session.count")
        print(res)

    async def lookup_session(self, topic_name):
        """
        Attempts to find the session id for a given topic

        http://crossbar.io/docs/Subscription-Meta-Events-and-Procedures/
        """
        res = await self.call("wamp.subscription.lookup", topic_name)
        print(res)


class Service(Eventify):
    """
    Create crossbar service
    """
    def start(self, start_loop=True):
        """
        Start a producer/consumer service
        """
        logger.debug('starting producer/consumer service')

        # Connect to crossbar
        runner = ApplicationRunner(
            url=self.config['transport_host'],
            realm=u'realm1',
            extra={
                'config': self.config,
                'handlers': self.handlers,
            }
        )
        if start_loop:
            runner.run(Component)
        else:
            return runner.run(Component, start_loop=start_loop)
