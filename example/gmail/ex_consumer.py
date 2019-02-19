"""
Example Gmail Consumer
"""
import asyncio
import json
import logging
import re
import time

from eventify.base_handler import BaseHandler
from eventify.drivers.gmail import Service
from eventify.event import Event

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('gce.vm.collector')

class Collector(BaseHandler):

    async def init(self):
        print("inited")

    async def on_event(self, event):
        # clean up event to make valid json
        event = event[:-1]
        event = event.replace('\\', '')
        event = event.replace('"[', '[')
        event = event.replace(']"', ']')
        event = event.replace('"BUD"', '')
        event = event.replace('"KIT"', '')
        event = event.replace('"CLEAVE"', '')
        event = event.replace('"BILL"', '')
        event = event.replace('"C"', '')
        event = event.replace('"ici": ,', '')
        event = event.replace('"AJ"', '')
        event = event.replace('"MIKE"', '')
        event = event.replace('"KEN"', '')
        print(event)
        decoded = json.loads(event)



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
