"""
Consumer module
"""
import tornado.gen

from eventify.stream import Stream


@tornado.gen.coroutine
def consumer(callback, topic='default', timeout=0, react_in=0):
    """
    Start listening to a stream
    :param callback: Callback function
    :param topic: Topic Name
    :param timeout: Timeout Seconds
    :param react_in: React Seconds
    """
    stream = Stream(topic=topic)
    stream.listen(callback, timeout, react_in)
