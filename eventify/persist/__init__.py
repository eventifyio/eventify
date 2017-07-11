"""
Persist Helper Module
"""
from __future__ import print_function
from datetime import datetime
from uuid import UUID

import asyncio
import asyncpg
import json
import logging
import os
import pytz

from eventify.exceptions import EventifySanityError


logger = logging.getLogger('eventify.persist')


async def persist_event(topic, event, pool):
    """
    Track event to prevent duplication of work
    and potential loss of event
    :param topic: The event topic
    :param event: The event object
    """
    # Event to json
    json_event = json.dumps(event.as_json())

    # Connect to database or create and connect if non existent
    conn = await pool.acquire()

    # Insert event if not processed
    try:
        utc = pytz.timezone('UTC')
        issued_at = utc.localize(datetime.utcnow())
        query = 'INSERT INTO %s (event, issued_at) VALUES ($1, $2)' % topic
        await conn.execute(query, json_event, issued_at)
    finally:
        await pool.release(conn)
