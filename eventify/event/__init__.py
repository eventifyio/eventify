"""
Event Module
"""
import json
import logging
from datetime import datetime
from uuid import uuid4

from eventify.persist import connect_pg
from eventify.persist.models import get_table


logger = logging.getLogger('eventify.event')


class Event(object):
    """
    Event object
    """

    def __init__(self, event, **kwargs):
        """
        Create event
        :param event: Dictionary object
        :param kwargs: allow for customizing event
        """
        self.name = event.get('name')
        self.timestamp = event.get('timestamp', str(datetime.utcnow()))
        self.trace_id = event.get('trace_id', str(uuid4()))
        self.event_id = event.get('event_id', str(uuid4()))

        if event.get('message') is not None:
            try:
                if isinstance(event['message'], dict):
                    self.message = json.dumps(event['message'])
                else:
                    self.message = event['message']
            except ValueError:
                self.message = event['message']

        if kwargs is not None:
            for (key, value) in kwargs.items():
                setattr(self, key, value)


    def as_json(self):
        """
        Convert to dictionary
        """
        return self.__dict__


def replay_events(subscribed_topics, timestamp=None, event_id=None):
    """
    Replay events from a given timestamp or event_id
    :param timestamp: Human readable datetime
    :param event_id: UUID of a given event
    """
    logger.debug("replaying events")
    engine = connect_pg('event_history')
    conn = engine.connect()
    for topic in subscribed_topics:
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
