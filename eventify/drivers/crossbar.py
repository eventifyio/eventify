"""
Crossbar Driver Module
"""
from __future__ import print_function

import asyncio
import logging
import sys
import time
import traceback
import txaio

import asyncpg

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory
from autobahn.wamp.types import SubscribeOptions, PublishOptions

from eventify.persist import persist_event
from eventify.persist.constants import EVENT_DB_HOST, EVENT_DB_USER, EVENT_DB_PASS, \
    EVENT_DB_NAME
from eventify import Eventify


txaio.use_asyncio()


class Component(ApplicationSession):
    """
    Handle subscribing to topics
    """
    log = logging.getLogger("eventify.drivers.crossbar")

    async def onConnect(self):
        """
        Configure the component
        """
        # setup transport host
        self.transport_host = self.config.extra['config']['transport_host']

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
        if self.config.extra['config']['pub_options']['retain'] is True:
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
        self.log.info("connected")
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
                return

        await self.publish(
            self.publish_topic,
            event.__dict__,
            options=self.publish_options
        )


    def onClose(self, wasClean):
        """
        Disconnect when connection to message
        broker is lost
        """
        self.log.error('lost connection to crossbar on session ' + str(self.session_id))
        loop = asyncio.get_event_loop()
        loop.stop()
        loop.close()


    async def onJoin(self, details):
        self.log.info("joined websocket realm: %s", details)

        # set session_id for reconnect
        self.session_id = details.session
        self.realm_id = details.realm

        for handler in self.handlers:
            # initialize handler
            handler_instance = handler()
            handler_instance.set_session(self)

            if hasattr(handler_instance, 'init'):
                await handler_instance.init()

            if hasattr(handler_instance, 'on_event'):
                self.log.info("subscribing to topic %s", handler_instance.subscribe_topic)

                # Used with base handler defined subscribe_topic
                if handler_instance.subscribe_topic is not None:
                    await self.subscribe(
                        handler_instance.on_event,
                        handler_instance.subscribe_topic,
                    )
                    self.log.info("subscribed to topic: %s", handler_instance.subscribe_topic)
                else:
                    # Used with config.json defined topics
                    if self.subscribed_topics is not None:
                        for topic in self.subscribed_topics:
                            await self.subscribe(
                                handler_instance.on_event,
                                topic
                            )
                            self.log.info("subscribed to topic: %s", topic)

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
    def setup_runner(self):
        """
        Setup instance of runner var
        """
        runner = ApplicationRunner(
            url=self.config['transport_host'],
            realm=u'realm1',
            extra={
                'config': self.config,
                'handlers': self.handlers,
            }
        )
        return runner


    def start(self, start_loop=True):
        """
        Start a producer/consumer service
        """
        txaio.start_logging(level='info')
        runner = self.setup_runner()
        if start_loop:

            # Initial connection
            try:
                runner.run(Component)
            except ConnectionRefusedError:
                logging.error('Unable to connect to crossbar instance. Is it running?')
                sys.exit(1)
            except KeyboardInterrupt:
                logging.info('User initiated shutdown')
                loop.get_event_loop()
                loop.stop()
                sys.exit(1)

            # Handle reconnect logic
            connect_attempt = 0
            max_retries = self.config['max_reconnect_retries']
            while True:

                # Stop service if unable to connect
                # after max retries is reached
                if connect_attempt == max_retries:
                    logging.info('max retries reached; stopping service')
                    sys.exit(1)

                # Setup new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    loop.run_until_complete(runner.run(Component))
                except RuntimeError as error:
                    logging.error(error)
                except ConnectionRefusedError as error:
                    logging.error(error)

                # Add delay for reconnect
                time.sleep(5)
                connect_attempt += 1

        else:
            return runner.run(
                Component,
                start_loop=start_loop
            )
