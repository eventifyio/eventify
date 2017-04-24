from eventify.producer import Producer

def send(producer, message):
    """
    send message on socket
    :param producer:
    :param message:
    """
    producer.send_message(message)


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
    send(producer, {"hi": "what"})
