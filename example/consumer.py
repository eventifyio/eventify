import json

from eventify.consumer import Consumer

def handler(event=None, **kwargs):
    """
    Handle events as they arrive
    :param event: Event
    :param kwargs: Keyword args
    """
    if event is not None:
        print(event)

    event_name = kwargs.get('name')
    event_body = json.loads(kwargs.get('message'))
    event_timestamp = kwargs.get('timestamp')
    print('Received event %s at %s with body: %s' % (event_name, event_timestamp, event_body))


if __name__ == '__main__':
    """
    Start the consumer service
    """
    print('Starting consumer...')
    consumer = Consumer(
        config_file='config.json',
        callback=handler
    )
    consumer.start()
