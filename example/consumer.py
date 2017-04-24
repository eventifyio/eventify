from eventify.consumer import Consumer


def handler(event=None, **kwargs):
    """
    Handle events as they arrive
    :param event: Event
    :param kwargs: Keyword args
    """
    if event is not None:
        print(event)

    print(kwargs)


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
