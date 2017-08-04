"""
Persist Helper Module
"""
from __future__ import print_function
from datetime import datetime

import json
import os

import asyncio
import asyncpg

from eventify.exceptions import EventifySanityError


async def persist_event(topic, event, pool):
    """
    Track event to prevent duplication of work
    and potential loss of event
    :param topic: The event topic
    :param event: The event object
    """
    # Event to json
    json_event = json.dumps(event.__dict__)

    # Connect to database or create and connect if non existent
    conn = await pool.acquire()

    # Insert event if not processed
    try:
        query = """
            CREATE TABLE IF NOT EXISTS public."topic_placeholder"
            (
              id SERIAL PRIMARY KEY,
              event json NOT NULL,
              issued_at timestamp without time zone NOT NULL
            )
            WITH (
              OIDS=FALSE
            );
            ALTER TABLE public."topic_placeholder"
              OWNER TO root;
        """
        query = query.replace('topic_placeholder', topic)
        await conn.execute(query)
        issued_at = datetime.utcnow()
        query = 'INSERT INTO "%s" (event, issued_at) VALUES ($1, $2)' % topic
        await conn.execute(query, json_event, issued_at)
    finally:
        await pool.release(conn)
