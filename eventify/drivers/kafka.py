"""
Kafka Driver Integration
"""
import asyncio
import json
import logging
import socket
import sys
import time
import traceback

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from asyncio import BaseProtocol

import txaio

from eventify import Eventify
from eventify.drivers.base import BaseComponent
from eventify.persist import persist_event
from eventify.persist.constants import EVENT_DB_HOST, EVENT_DB_USER, EVENT_DB_PASS, \
    EVENT_DB_NAME


txaio.use_asyncio()


class Component(BaseComponent):
    """
    Handle subscribing to topics
    """
    log = logging.getLogger("eventify.drivers.kafka")

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

        loop = asyncio.get_event_loop()
        producer = AIOKafkaProducer(
            loop=loop,
            bootstrap_servers=self.transport_host
        )
        await producer.start()

        try:
            event = json.dumps(event.__dict__).encode()
            await producer.send_and_wait(
                self.publish_topic,
                event
            )
        finally:
            await producer.stop()

    async def onJoin(self):
        loop = asyncio.get_event_loop()

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
                    consumer = AIOKafkaConsumer(
                        handler_instance.subscribe_topic,
                        bootstrap_servers=self.transport_host,
                        loop=loop
                    )
                    await consumer.start()
                    self.log.debug("subscribed to topic: %s", handler_instance.subscribe_topic)

                    try:
                        async for msg in consumer:
                            await handler_instance.on_event(msg.value)
                    finally:
                        await consumer.stop()
                else:
                    # Used with config.json defined topics
                    if self.subscribed_topics is not None:
                        consumer = AIOKafkaConsumer(
                            bootstrap_servers=self.transport_host,
                            loop=loop,
                            group_id='my-group'
                        )
                        await consumer.start()

                        # Subscribe to all topics
                        for topic in self.subscribed_topics:
                            consumer.subscribe(topic)

                        try:
                            async for msg in consumer:
                                value = msg.value.decode()
                                await handler_instance.on_event(value)
                        except Exception as error:
                            self.log.error("Consumer error. %s", error)
                            await asyncio.sleep(0)

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
    Create kafka service
    """

    def start(self):
        """
        Start a producer/consumer service
        """
        component = Component(self.config, self.handlers)
        component.run()
