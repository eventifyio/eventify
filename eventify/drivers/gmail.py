"""
Gmail Driver Module
"""
from __future__ import print_function
from email.mime.text import MIMEText

import aiosmtplib
import asyncio
import json
import logging
import os
import re
import socket
import sys
import time
import traceback
import txaio

from aioimaplib import aioimaplib

from eventify import Eventify
from eventify.drivers.base import BaseComponent
from eventify.persist import persist_event
from eventify.persist.constants import EVENT_DB_HOST, EVENT_DB_USER, EVENT_DB_PASS, \
    EVENT_DB_NAME


txaio.use_asyncio()

# You should probably use oauth but this driver
# is not meant for production use but only for
# a local tutorial
#
# If you wish to use this driver. Please note that
# you will need to enable "Less secure apps" on the
# google account you attempt to use.
GMAIL_USERNAME = os.getenv('GMAIL_USERNAME')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')


class Component(BaseComponent):
    """
    Handle subscribing to topics
    """
    log = logging.getLogger("eventify.drivers.gmail")

    def __init__(self, config, handlers):
        self.config = config
        self.handlers = handlers

    def run(self):
        """
        start component
        """
        self.loop = asyncio.get_event_loop()
        if self.loop.is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
            self.loop = asyncio.get_event_loop()

        txaio.start_logging()
        self.loop.run_until_complete(self.onConnect())

    async def onConnect(self):
        """
        Inherited from BaseComponent
        auth with gmail
        """
        await super().onConnect()
        self.smtp = aiosmtplib.SMTP(
            hostname="smtp.gmail.com",
            port=465,
            loop=self.loop,
            use_tls=True
        )
        await self.smtp.connect()
        await self.smtp.login(username=GMAIL_USERNAME, password=GMAIL_PASSWORD)
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

        # serialize
        data = json.dumps(event.__dict__)

        # test message
        message = MIMEText(data)
        message["From"] = "eventify.service.app@gmail.com"
        message["To"] = "eventify.service.app@gmail.com"
        message["Subject"] = "Test Message"

        # send message
        await self.smtp.send_message(message)

    async def onJoin(self):
        self.log.info("connected to gmail")

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
                    self.log.debug("subscribed to topic: %s", handler_instance.subscribe_topic)
                    while True:
                        imap_client = aioimaplib.IMAP4_SSL(host='imap.gmail.com')
                        await imap_client.wait_hello_from_server()
                        await imap_client.login(GMAIL_USERNAME, GMAIL_PASSWORD)
                        res, data = await imap_client.select()
                        print('there is %s messages INBOX' % data[0])
                    #while True: - get msg from gmail and send to handler
                    #    msg = await session.recv_multipart()
                    #    await handler_instance.on_event(msg)
                else:
                    # Used with config.json defined topics
                    if self.subscribed_topics is not None:
                        # test
                        imap_client = aioimaplib.IMAP4_SSL(host='imap.gmail.com')
                        await imap_client.wait_hello_from_server()
                        await imap_client.login(GMAIL_USERNAME, GMAIL_PASSWORD)
                        res, data = await imap_client.select()
                        if res == 'OK':
                            result, emails = await imap_client.fetch('20', 'BODY[]')
                            if result == 'OK':
                                body_pattern = re.compile('Subject:[^{]*(.*)}')
                                for mail in emails:
                                    groups = re.search(body_pattern, str(mail))
                                    if groups:
                                        json_message = groups[1]
                                        await handler_instance.on_event(json_message)
                                        
                        else:
                            raise Exception("Failed to connect to gmail")

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
    Create gmail service
    """

    def start(self):
        """
        Start a producer/consumer service
        """
        component = Component(self.config, self.handlers)
        component.run()
