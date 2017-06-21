"""
Service Module
"""
from __future__ import print_function

import logging

from autobahn.twisted.wamp import Session, ApplicationRunner
from autobahn.wamp.types import SubscribeOptions, PublishOptions
from sqlalchemy import select
from twisted.internet.defer import inlineCallbacks

from eventify import Eventify
from eventify.persist import persist_event, connect_pg
from eventify.persist.models import get_table


logger = logging.getLogger('eventify.service')


class Component(Session):
    """
    Handle subscribing to topics
    """

    def publish(self, topic, event, options=None):
        """
        Override publish method to support
        event store pattern
        """
        if self.config.extra['config']['pub_options']['retain']:
            try:
                persist_event(topic, event)
            except SystemError as error:
                logger.error(error)
                return

        super().publish(
            topic,
            event.as_json(),
            options=options
        )


    def onConnect(self):
        """
        Configure the component
        """

        # subscription setup
        self.subcribed_topics = self.config.extra['config']['subscribed_topics']
        self.subscribe_options = SubscribeOptions(**self.config.extra['config']['sub_options'])

        # publishing setup
        self.publish_topic = self.config.extra['config']['publish_topic']['topic']
        self.publish_options = PublishOptions(**self.config.extra['config']['pub_options'])

        # join topic
        self.callback = self.config.extra['callback']
        self.join(self.config.realm)


    @inlineCallbacks
    def emit_event(self, event):
        """
        Publish an event back to crossbar
        :param event: Event object
        """
        yield self.publish(
            self.publish_topic,
            event,
            options=self.publish_options
        )


    @inlineCallbacks
    def onJoin(self, details):
        logger.debug("session attached: %s", details)

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


            self.callback(event, session=self)

        for topic in self.subcribed_topics:
            pub = yield self.subscribe(
                transport_event,
                topic,
                options=self.subscribe_options
            )

            # Use crossbar support for replaying events
            # vs using an event store
            if self.config.extra['config']['replay_events']:
                events = yield self.call(u"wamp.subscription.get_events", pub.id, 1000)
                for event in reversed(events):
                    transport_event(event)


class Service(Eventify):
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
        runner.run(Component, auto_reconnect=True)


    def replay_events(self, timestamp=None, event_id=None):
        """
        Instantiate object
        :param timestamp: Human readable datetime
        :param event_id: UUID of a given event
        """
        engine = connect_pg('event_history')
        conn = engine.connect()
        table = get_table(self.config['publish_topic']['topic'], engine)
        query = table.select()
        if timestamp is not None and event_id is not None:
            raise ValueError("Can only filter by timestamp OR event_id")
        elif timestamp is not None:
            query = query.where(table.c.issued_at >= timestamp)
        elif event_id is not None:
            get_id_query = table.select(table.c.event['event_id'].astext == event_id)
            row = conn.execute(get_id_query).fetchone()
            row_id = row[0]
            query = query.where(table.c.id > row_id)

        result = conn.execute(query).fetchall()
        for row in result:
            yield row[1]
