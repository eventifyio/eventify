import logging
import sys

from eventify.event import Event
from eventify.producer import Producer


FORMAT = '%(asctime)-15s %(name)s %(levelname)s %(message)s'
logging.basicConfig(stream=sys.stdout, format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger('example.producer')
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    logger.info('service initializing')
    producer = Producer(
        config_file='config.json'
    )
    event = Event('TestEvent', {'foo': 'bar'})
    producer.emit_event(event)
