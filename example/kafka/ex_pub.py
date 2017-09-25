"""
ZeroMQ Example Message Transport
"""
import asyncio
import logging
import time

from eventify.base_handler import BaseHandler
from eventify.drivers.kafka import Service
from eventify.event import Event

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('gce.vm.collector')


class Collector(BaseHandler):

    async def init(self):
        while True:
            event = Event({
                'name': 'HelloWorld',
                'message': 'Hi!'
            })
            await self.session.emit_event(event)
            time.sleep(1)

def run():
    """
    Run an eventify service
    """
    Service(
        config_file='config.json',
        handlers=[Collector]
    ).start()

if __name__ == '__main__':
    run()
