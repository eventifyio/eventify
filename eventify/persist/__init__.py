"""
Persist Helper Module
"""
from __future__ import print_function
from datetime import datetime

import asyncio
import asyncpg
import json
import os

from eventify.exceptions import EventifySanityError


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
        issued_at = datetime.utcnow()
        query = 'INSERT INTO "%s" (event, issued_at) VALUES ($1, $2)' % topic
        await conn.execute(query, json_event, issued_at)
    finally:
        await pool.release(conn)
