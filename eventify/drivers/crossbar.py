"""
Crossbar Driver Module
"""
from __future__ import print_function

import logging

from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import SubscribeOptions, PublishOptions
from sqlalchemy import select
from twisted.internet.defer import inlineCallbacks

from eventify import Eventify
from eventify.persist import persist_event, connect_pg
from eventify.persist.models import get_table


logger = logging.getLogger('eventify.drivers.crossbar')


class Component(ApplicationSession):
    """
    Handle subscribing to topics
    """

    def onConnect(self):
        """
        Configure the component
        """

        # subscription setup
        self.subscribed_topics = self.config.extra['config']['subscribed_topics']
        self.subscribe_options = SubscribeOptions(**self.config.extra['config']['sub_options'])

        # publishing setup
        self.publish_topic = self.config.extra['config']['publish_topic']['topic']
        self.publish_options = PublishOptions(**self.config.extra['config']['pub_options'])

        # setup callback
        self.callback = self.config.extra['callback']

        # config producer
        try:
            self.producer = self.config.extra['producer']
        except KeyError:
            self.producer = None

        # join topic
        self.join(self.config.realm)


    @inlineCallbacks
    def emit_event(self, event):
        """
        Publish an event back to crossbar
        :param event: Event object
        """
        logger.debug("publishing event on %s", self.publish_topic)
        if self.config.extra['config']['pub_options']['retain']:
            try:
                logger.debug("persisting event")
                persist_event(self.publish_topic, event)
                logger.debug("event persisted")
            except SystemError as error:
                logger.error(error)
                return

            published = self.publish(
                self.publish_topic,
                event.as_json(),
                options=self.publish_options
            )
            logger.debug("event published")
            yield published


    @inlineCallbacks
    def onJoin(self, details):
        logger.debug("joined websocket realm: %s", details)


        def transport_event(*args, **kwargs):
            """
            Send event to application code
            """
            try:
                event = args[0]['kwargs']
            except KeyError as error:
                if kwargs == {}:
                    event = args[0]
                else:
                    event = kwargs
            except IndexError as error:
                event = kwargs
            logger.debug("received event %s", event['event_id'])
            self.callback(event, session=self)


        if self.producer:
            logger.debug("detected producer only service")
            self.callback(self)


        # Subscribe to all of the topics in configuration
        if self.producer is None:
            for topic in self.subscribed_topics:
                logger.debug("subscribing to topic %s", topic)
                yield self.subscribe(
                    transport_event,
                    topic,
                )
                logger.debug("subscribed to topic: %s", topic)


    @inlineCallbacks
    def show_sessions(self):
        """
        Returns an object with a lists of the session IDs
        for all sessions currently attached to the realm

        http://crossbar.io/docs/Session-Metaevents-and-Procedures/
        """
        res = yield self.call("wamp.session.list")
        for session_id in res:
            info = yield self.call("wamp.session.get", session_id)
            print(info)


    @inlineCallbacks
    def total_sessions(self):
        """
        Returns the number of sessions currently attached to the realm.

        http://crossbar.io/docs/Session-Metaevents-and-Procedures/
        """
        res = yield self.call("wamp.session.count")
        print(res)


    def replay_events(self, timestamp=None, event_id=None):
        """
        Replay events from a given timestamp or event_id
        :param timestamp: Human readable datetime
        :param event_id: UUID of a given event
        """
        engine = connect_pg('event_history')
        conn = engine.connect()
        for topic in self.subscribed_topics:
            logger.debug("replaying events for topic %s", topic)
            table = get_table(topic, engine)
            query = table.select()
            if timestamp is not None and event_id is not None:
                raise ValueError("Can only filter by timestamp OR event_id")
            elif timestamp is not None:
                query = query.where(table.c.issued_at >= timestamp)
            elif event_id is not None:
                get_id_query = table.select(table.c.event['event_id'].astext == event_id)
                row = conn.execute(get_id_query).fetchone()
                if row is not None:
                    row_id = row[0]
                    query = query.where(table.c.id > row_id)
            result = conn.execute(query).fetchall()
            for row in result:
                yield row[1]


def create_service():

    class Service(object):
        """
        Create crossbar service
        """

        def __init__(self, config, callback):
            self.config = config
            self.callback = callback


        def start(self):
            """
            Start a producer/consumer service
            """
            logger.debug('starting producer/consumer service')
            runner = ApplicationRunner(
                url=self.config['transport_host'],
                realm=u'realm1',
                extra={
                    'config': self.config,
                    'callback': self.callback
                }
            )
            runner.run(Component, auto_reconnect=True)


        def start_producer(self):
            """
            Start a pure producer service
            """
            logger.debug('starting producer service')
            runner = ApplicationRunner(
                url=self.config['transport_host'],
                realm=u'realm1',
                extra={
                    'config': self.config,
                    'producer': True,
                    'callback': self.callback
                }
            )
            runner.run(Component, auto_reconnect=True)

    return Service
