"""
Crossbar Driver Module
"""
from __future__ import print_function

import asyncio

import sys
import traceback
import txaio

import asyncpg

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import SubscribeOptions, PublishOptions

from eventify.persist import persist_event
from eventify.persist.constants import EVENT_DB_HOST, EVENT_DB_USER, EVENT_DB_PASS, \
    EVENT_DB_NAME
from eventify import Eventify


class Component(ApplicationSession):
    """
    Handle subscribing to topics
    """
    log = txaio.make_logger()

    async def onConnect(self):
        """
        Configure the component
        """

        # subscription setup
        self.subscribe_options = SubscribeOptions(**self.config.extra['config']['sub_options'])
        self.replay_events = self.config.extra['config']['replay_events']

        # publishing setup
        self.publish_topic = self.config.extra['config']['publish_topic']['topic']
        self.publish_options = PublishOptions(**self.config.extra['config']['pub_options'])

        # setup callback
        self.handlers = self.config.extra['handlers']

        # optional subscribed topics from config.json
        self.subscribed_topics = self.config.extra['config']['subscribed_topics']

        # put name on session
        self.name = self.config.extra['config']['name']

        # setup db pool - optionally
        if self.publish_options['retain'] is True:
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
        self.log.debug("connected")
        self.join(self.config.realm)

    async def emit_event(self, event):
        """
        Publish an event back to crossbar
        :param event: Event object
        """
        self.log.debug("publishing event on %s", self.publish_topic)
        if self.config.extra['config']['pub_options']['retain']:
            try:
                await persist_event(
                    self.publish_topic,
                    event,
                    self.pool
                )
            except SystemError as error:
                self.log.error(error)
                self.log.error(error)
                return

        await self.publish(
            self.publish_topic,
            event.__dict__,
            options=self.publish_options
        )

    def onClose(self, wasClean, code, reason):
        """
        Auto reconnect with crossbar if connection
        is lost
        """
        self.log.error(wasClean)
        self.log.error(code)
        self.log.error(reason)

        loop = asyncio.get_event_loop()
        loop.stop()
        raise ConnectionError("Lost connection to crossbar")


    async def onJoin(self, details):
        self.log.debug("joined websocket realm: %s", details)

        for handler in self.handlers:
            # initialize handler
            handler_instance = handler()
            handler_instance.set_session(self)

            if hasattr(handler_instance, 'init'):
                await handler_instance.init()

            if hasattr(handler_instance, 'on_event'):
                self.log.debug("subscribing to topic %s", handler_instance.subscribe_topic)

                # Used with base handler defined subscribe_topic
                if handler_instance.subscribe_topic is not None:
                    await self.subscribe(
                        handler_instance.on_event,
                        handler_instance.subscribe_topic,
                    )
                    self.log.debug("subscribed to topic: %s", handler_instance.subscribe_topic)
                else:
                    # Used with config.json defined topics
                    if self.subscribed_topics is not None:
                        for topic in self.subscribed_topics:
                            await self.subscribe(
                                handler_instance.on_event,
                                topic
                            )
                            self.log.debug("subscribed to topic: %s", topic)

            if hasattr(handler_instance, 'worker'):
                # or just await handler.worker()
                while True:
                    try:
                        await handler_instance.worker()
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
        # Connect to crossbar
        runner = ApplicationRunner(
            url=self.config['transport_host'],
            realm=u'realm1',
            extra={
                'config': self.config,
                'handlers': self.handlers,
            }
        )
        self.run_component(runner, start_loop)


    def run_component(self, runner, start_loop=True):
        """
        Support autoconnecting for asyncio
        and cross bar
        """
        try:
            if start_loop:
                runner.run(Component)
            else:
                return runner.run(Component, start_loop=start_loop)
        except ConnectionError:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    asyncio.set_event_loop(asyncio.new_event_loop())
                    self.run_component(runner, start_loop)
            except Exception as error:
                print(error)
                sys.exit(1)
