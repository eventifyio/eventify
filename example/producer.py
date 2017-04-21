from eventify.producer import Producer

if __name__ == '__main__':
    """
    Start the producer service
    """
    print('Starting UI event message producer...')
    producer = Producer(config_file='config.json')
    producer.start()
