import tornado.gen
import tornado.ioloop

from eventify.stream import Stream
from service import EventHandler


@tornado.gen.coroutine
def consume():
    """
    Connect to stream and watch events

    Args:
        topic (basestring): Which topic were listening to
        timeout (int): Visibility of message
        react_in (int): Delay reaction to event
    """
    stream = EventHandler(config='consumer-config.json')
    topics = stream.topics_subscribed_to

    for topic in topics:
        name = topic['topic']
        timeout = topic['timeout']
        react_in = topic['reply_in']
        new_stream = EventHandler(config='consumer-config.json', topic=name)
        yield new_stream.listen(new_stream.process_event, timeout, react_in)


def done_callback(future):
    """
    Called when tornado finishes async call
    """
    future.result()


if __name__ == '__main__':
    try:
        future = consume()
        future.add_done_callback(done_callback)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        import sys
        sys.exit()
