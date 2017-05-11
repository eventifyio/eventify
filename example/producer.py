from eventify.event import Event
from eventify.producer import Producer

def send(producer, event):
    """
    send message on socket
    :param producer:
    :param message:
    """
    producer.emit_event(event)

def run(producer):
    """
    Start producer
    """
    producer.start()

if __name__ == '__main__':
    """
    Start the producer service
    """
    print('Starting UI event message producer...')
    producer = Producer(config_file='config.json')
    event = Event('TestEvent', {"foo": "bar"})
    send(producer, event)
