#!/usr/bin/env python
"""
Minimal viable microservice that publishes events
to test how system works
"""
import logging
import sys

from eventify.event import Event
from eventify.service import Service


FORMAT = '%(asctime)-15s %(name)s %(levelname)s %(message)s'
logging.basicConfig(stream=sys.stdout, format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger('event.producer')

async def display_stats(session):
    # show all session data
    await session.show_sessions()

    # show total sessions
    await session.total_sessions()

    # lookup session
    await session.lookup_session('example')

if __name__ == '__main__':
    service = Service(config_file='config-manage.json', callback=display_stats)
    service.start_producer()
