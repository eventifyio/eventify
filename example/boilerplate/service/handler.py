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

    async def init(self):
        """
        Service initialization
        """
        await self.session.show_sessions()
