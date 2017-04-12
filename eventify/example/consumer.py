import tornado.gen
import tornado.ioloop

from eventify.stream import Stream
from service import EventHandler


@tornado.gen.coroutine
def consume(topic='default', timeout=20, react_in=0):
    """
    Connect to stream and watch events

    Args:
        topic (basestring): Which topic were listening to
        timeout (int): Visibility of message
        react_in (int): Delay reaction to event
    """
    stream = EventHandler(topic=topic, config='config.json')
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
