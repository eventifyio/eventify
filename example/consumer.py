from eventify.consumer import Consumer

if __name__ == '__main__':
    """
    Start the consumer service
    """
    print('Starting consumer...')
    consumer = Consumer(config_file='config.json')
    consumer.start()
