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

def display_stats(session):
    # show all session data
    session.show_sessions()

    # show total sessions
    #session.total_sessions()




if __name__ == '__main__':
    service = Service(config_file='config-producer.json', callback=display_stats)
    service.start_producer()
