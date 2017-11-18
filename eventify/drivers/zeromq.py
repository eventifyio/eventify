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

from asyncio import BaseProtocol

import txaio
import zmq
import zmq.asyncio

from eventify import Eventify
from eventify.drivers.base import BaseComponent
from eventify.persist import persist_event
from eventify.persist.constants import EVENT_DB_HOST, EVENT_DB_USER, EVENT_DB_PASS, \
    EVENT_DB_NAME


txaio.use_asyncio()
ctx = zmq.asyncio.Context.instance()


class Component(BaseComponent):
    """
    Handle subscribing to topics
    """
    log = logging.getLogger("eventify.drivers.zeromq")

    def __init__(self, config, handlers):
        self.config = config
        self.handlers = handlers

    def run(self):
        """
        start component
        """
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()

        txaio.start_logging()
        loop.run_until_complete(self.onConnect())

    async def onConnect(self):
        """
        Inherited from BaseComponent
        """
        await super().onConnect()
        self.log.info("connected")
        await self.onJoin()

    async def emit_event(self, event):
        """
        Publish an event
        :param event: Event object
        """
        self.log.info("publishing event on %s", self.publish_topic)
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

        await asyncio.sleep(1)

    async def onJoin(self):
        self.log.info("connected to zmq")

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
                    session = ctx.socket(zmq.SUB)
                    session.connect(self.transport_host)
                    session.subscribe(handler_instance.subscribe_topic)
                    self.log.debug("subscribed to topic: %s", handler_instance.subscribe_topic)
                    while True:
                        msg = await session.recv_multipart()
                        await handler_instance.on_event(msg)
                else:
                    # Used with config.json defined topics
                    if self.subscribed_topics is not None:
                        session = ctx.socket(zmq.SUB)
                        session.connect(self.transport_host)
                        for topic in self.subscribed_topics:
                            session.subscribe(topic)
                            self.log.info("subscribed to topic: %s", topic)
                        while True:
                            msg = await session.recv_multipart()
                            self.log.info('got msg %s', msg)
                            await handler_instance.on_event(msg)

            if hasattr(handler_instance, 'worker'):
                while True:
                    try:
                        await handler_instance.worker()
                    except Exception as error:
                        self.log.error("Operation failed. %s", error)
                        traceback.print_exc(file=sys.stdout)
                        continue


class Service(Eventify):
    """
    Create zeromq service
    """

    def check_transport_host(self):
        """
        Check if zeromq socket is available
        on transport host
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('events-server', 8080))
        if result == 0:
            logging.info('port 8080 on zmq is open!')
            return True
        return False

    def start(self):
        """
        Start a producer/consumer service
        """
        component = Component(self.config, self.handlers)
        component.run()
