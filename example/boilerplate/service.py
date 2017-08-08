"""
Constantly poll AWS for usage for customer data
"""
import logging

from eventify.service import Service

from service.handler import Collector

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('gce.vm.collector')


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
