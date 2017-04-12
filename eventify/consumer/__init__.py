"""
Consumer module
"""
import tornado.gen

from eventify.stream import Stream


@tornado.gen.coroutine
def consumer(callback, topic='default', timeout=0, react_in=0):
    """
    Start listening to a stream

    Args:
        callback (func): Callback function
        topic (str): Topic Name
        timeout (int): Timeout Seconds
        react_in (int): React Seconds
    """
    stream = Stream(topic=topic)
    stream.listen(callback, timeout, react_in)
