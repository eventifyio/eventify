"""
ZeroMQ Example Message Transport
"""
import asyncio
import logging

from eventify.base_handler import BaseHandler
from eventify.drivers.kafka import Service

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('gce.vm.collector')


class Collector(BaseHandler):

    async def on_event(self, event):
        print(event)
        await asyncio.sleep(0)

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
