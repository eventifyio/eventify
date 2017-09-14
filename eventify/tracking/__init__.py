"""
Event Tracking Module
"""
from datetime import datetime

import asyncio
import json

import aioredis

from eventify.tracking.constants import EVENT_TRACKING_HOST


loop = asyncio.get_event_loop()

async def track_event(event, state, service_name):
    """
    Store state of events in memory
    :param event: Event object
    :param state: EventState object
    :param service_name: Name of service name
    """
    redis = await aioredis.create_redis(
        (EVENT_TRACKING_HOST, 6379), loop=loop)

    now = datetime.utcnow()
    event_id = event.event_id

    tracking_data = json.dumps({
        "event_id": event_id,
        "timestamp": str(now),
        "state": state
    })
    await redis.rpush(service_name, tracking_data)
    redis.close()
    await redis.wait_closed()
