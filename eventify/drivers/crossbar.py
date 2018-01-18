"""
Crossbar Driver Module
"""
from __future__ import print_function

import asyncio
import logging
import socket
import sys
import time
import traceback
import txaio

import asyncpg

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.exception import TransportLost

from eventify import Eventify
from eventify.drivers.base import BaseComponent
from eventify.persist import persist_event
from eventify.exceptions import EventifyHandlerInitializationFailed


txaio.use_asyncio()


class Component(BaseComponent, ApplicationSession):
    """
    Handle subscribing to topics
    """
    log = logging.getLogger("eventify.drivers.crossbar")

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

        try:
            await self.publish(
                self.publish_topic,
                event.__dict__,
                options=self.publish_options
            )
        except TransportLost as error:
            for task in asyncio.Task.all_tasks():
                task.cancel()
            asyncio.get_event_loop().stop()
            self.log.error(error)

    def onClose(self, wasClean):
        """
        Disconnect when connection to message
        broker is lost
        """
        self.log.error('lost connection to crossbar on session %' + str(self.session_id))
        for task in asyncio.Task.all_tasks():
            task.cancel()
        asyncio.get_event_loop().stop()

    def onDisconnect(self):
        """
        Event fired when transport is lost
        """
        self.log.error('onDisconnect event fired')

    def onLeave(self, reason=None, message=None):
        """
        :param reason:
        :param message:
        """
        self.log.info('Leaving realm; reason: %s', reason)

    def onUserError(self, fail, message):
        """
        Handle user errors
        """
        self.log.error(fail)
        self.log.error(message)

    async def onJoin(self, details):
        self.log.debug("joined websocket realm: %s", details)

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
                    except Exception as error:
                        self.log.error("Operation failed. %s", error)
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
            self.log.info(session)

    async def total_sessions(self):
        """
        Returns the number of sessions currently attached to the realm.

        http://crossbar.io/docs/Session-Metaevents-and-Procedures/
        """
        res = await self.call("wamp.session.count")
        self.log.info(res)

    async def lookup_session(self, topic_name):
        """
        Attempts to find the session id for a given topic

        http://crossbar.io/docs/Subscription-Meta-Events-and-Procedures/
        """
        res = await self.call("wamp.subscription.lookup", topic_name)
        self.log.info(res)


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

    def check_transport_host(self):
        """
        Check if crossbar port is open
        on transport host
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('events-server', 8080))  # TODO: Read from config vs using hard coded hostname
        if result == 0:
            logging.info('port 8080 on crossbar is open!')
            return True
        return False

    def reconnect(self):
        """
        Handle reconnect logic if connection
        to crossbar is lost
        """
        connect_attempt = 0
        max_retries = self.config['max_reconnect_retries']
        logging.info('attempting to reconnect to crossbar')
        runner = self.setup_runner()
        while True:

            if connect_attempt == max_retries:
                logging.info('max retries reached; stopping service')
                sys.exit(1)
            self.check_event_loop()

            try:
                logging.info('waiting 5 seconds')
                time.sleep(5)
                if self.check_transport_host():
                    logging.info('waiting 10 seconds to ensure that crossbar has initialized before reconnecting')
                    time.sleep(10)
                    runner.run(Component)
                else:
                    logging.error('crossbar host port 8080 not available...')
            except RuntimeError as error:
                logging.error(error)
            except ConnectionRefusedError as error:
                logging.error(error)
            except ConnectionError as error:
                logging.error(error)
            except KeyboardInterrupt:
                logging.info('User initiated shutdown')
                loop = asyncio.get_event_loop()
                loop.stop()
                sys.exit(1)
            connect_attempt += 1

    def start(self, start_loop=True):
        """
        Start a producer/consumer service

        """
        txaio.start_logging()
        runner = self.setup_runner()
        if start_loop:
            try:
                runner.run(Component)
            except EventifyHandlerInitializationFailed as initError:
                logging.error('Unable to initialize handler: %s.' % initError.message)
                sys.exit(1)
            except ConnectionRefusedError:
                logging.error('Unable to connect to crossbar instance. Is it running?')
                sys.exit(1)
            except KeyboardInterrupt:
                logging.info('User initiated shutdown')
                loop = asyncio.get_event_loop()
                loop.stop()
                sys.exit(1)
            self.check_event_loop()
            self.reconnect()
        else:
            return runner.run(
                Component,
                start_loop=start_loop
            )
