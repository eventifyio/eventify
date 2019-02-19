"""
Example Gmail Publisher
"""
import aiohttp
import aiofiles
import asyncio
import json
import logging
import re
import time
import zipfile

from bs4 import BeautifulSoup as bs

from eventify.base_handler import BaseHandler
from eventify.drivers.gmail import Service
from eventify.event import Event

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('gce.vm.collector')

FEC_DATA_BASE = 'https://www.fec.gov'
FEC_DATA_URL = 'https://www.fec.gov/data/browse-data/?tab=bulk-data'
PATTERN = re.compile('.*weball.*')

class Collector(BaseHandler):

    @staticmethod
    async def fetch(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    @staticmethod
    async def download_and_parse(url):
        chunk_size = 5 * 2**20
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data_to_read = True
                while data_to_read:
                    data = bytearray()
                    red = 0
                    while red < chunk_size:
                        chunk = await response.content.read(chunk_size - red)
                        if not chunk:
                            data_to_read = False
                            break
                        data.extend(chunk)
                        red += len(chunk)
               
                    # write the zipfile to disk
                    async with aiofiles.open('filename_tmp.zip', 'wb') as f:
                        await f.write(data)

                    with zipfile.ZipFile('filename_tmp.zip', 'r') as zh:
                        zh.extractall()
                        files = zh.filelist
                        for filename in files:
                            print(filename.filename)
                            async with aiofiles.open(filename.filename, 'r') as f:
                                data = await f.read()
                                lines = data.split("\n")
                                all_info = []
                                for line in lines:
                                    # definition of fields
                                    # https://www.fec.gov/campaign-finance-data/all-candidates-file-description/
                                    raw = line.split('|')
                                    try:
                                        all_info.append({
                                            "id": raw[0],
                                            "name": raw[1],
                                            "ici": raw[2],
                                            "pty_cd": raw[3],
                                            "affiliation": raw[4],
                                            "ttl_receipts": raw[5],
                                            "trans_from_auth": raw[6],
                                        })
                                    except Exception as error:
                                        print(error)
                                return all_info

    async def init(self):
        data = await self.fetch(FEC_DATA_URL)
        soup = bs(data, 'html.parser')
        links = soup.find_all(href=True)
        for link in links:
            href = link['href']
            if re.match(PATTERN, href):
                data_url = FEC_DATA_BASE + href
                parsed_data = await self.download_and_parse(data_url)
                event = Event({
                    'name': 'Candidate Information',
                    'message': parsed_data
                })
                await self.session.emit_event(event)

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
