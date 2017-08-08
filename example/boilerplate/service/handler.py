"""
Collect GCE VM Data Points
and publish events in normalized structure
"""
import asyncio

from eventify.base_handler import BaseHandler
from eventify.event import Event

class GoogleCollector:
    """
    Google Specific Collector
    """
    async def collect_vm_data(self):
        print('...collecting data from gce api...')
        await asyncio.sleep(1)

class Collector(BaseHandler, GoogleCollector):
    """
    Generic collector
    """

    def __init__(self):
        """
        Service initialization
        """
        print('...service initialized...')

    async def worker(self):
        """
        Collect data for required data points
        https://bpaste.net/show/044ae52dc5bb
        """
        print('...working...')
        await self.collect_vm_data()
        await asyncio.sleep(5)


