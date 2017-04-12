import tornado.gen
import tornado.ioloop

from eventify.stream import Stream


@tornado.gen.coroutine
def provision_node(message):
    """
    Pseudo func

    Args:
        message (json): Message
    """
    print('NodeProvisioned')


@tornado.gen.coroutine
def start_node(message):
    """
    Pseudo func

    Args:
        message(json): Message
    """
    print('NodeStarted')


# Setup map of events to functions to process that event
events_to_process = {
    "NodeProvisionRequested": provision_node,
    "NodeStartRequested": start_node
}

class MyStream(Stream):
    """
    Create custom stream to process events
    """

    @tornado.gen.coroutine
    def process_event(self, event_id, message):
        """
        Process events from stream

        Args:
            event (json): Json representation of an event
        """
        event_name = message['event']
        if event_name in events_to_process:
            if events_to_process[event_name](message):
                self.delete_event(event_id)


@tornado.gen.coroutine
def consume(topic='default', timeout=20, react_in=0):
    """
    Connect to stream and watch events

    Args:
        topic (basestring): Which topic were listening to
        timeout (int): Visibility of message
        react_in (int): Delay reaction to event
    """
    stream = MyStream(topic=topic)
    stream.listen(stream.process_event, timeout, react_in)


def done_callback(future):
    """
    Called when tornado finishes async call
    """
    future.result()


if __name__ == '__main__':
    try:
        # Setup consumer
        topic = 'dev'

        future = consume(topic=topic)
        future.add_done_callback(done_callback)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        import sys
        sys.exit()
