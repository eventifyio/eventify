"""
Handle Stream Related Functions
"""
import json
import time

import beanstalkt
import tornado.gen

from eventify import Eventify
from eventify.persist import persist_event

class Stream(Eventify):
    """
    The stream object
    """

    def __init__(self, host='localhost', topic='default', driver='beanstalkd', **kwargs):
        """
        Constructor method

        Args:
            host (str): Hostname
            topic (str): Topic Name
            driver (str): Name of driver the service wants to use
        """
        self.host = host
        self.topic = topic
        self.driver = driver

        if driver == 'beanstalkt':
            self.client = beanstalkt.Client(host=self.host)
            self.connect()

        super(Stream, self).__init__(**kwargs)


    def connect(self):
        """
        Connect to stream
        """
        yield self.client.connect()
        yield self.client.use(self.topic)


    @tornado.gen.coroutine
    def listen(self, callback, timeout=0, react_in=0):
        """
        Start listening to a stream

        Args:
            timeout (int): Seconds to prevent other workers from reading event
        """
        if self.driver == 'beanstalkt':
            yield self.client.watch(self.topic)

            while True:
                event = yield self.client.reserve(timeout=timeout)
                if react_in != 0:
                    time.sleep(react_in)
                callback(event)
        else:
            raise ValueError("Stream driver not supported: %s" % self.driver)


    @tornado.gen.coroutine
    def emit_event(self, event, persist=True):
        """
        Emit event to stream

        Args:
            event (dict): Dictionary
            persist (bool): Persist to persistant store
        """
        if self.driver == 'beanstalkt':
            if persist:
                # Write to persistant store
                persist_event(event)

            # Convert string to bytes
            payload = str.encode(json.dumps(event))
            yield self.client.put(payload)


    @tornado.gen.coroutine
    def delete_event(self, event_id):
        """
        Delete event from stream

        Args:
            event_id (int): ID of event
        """
        if self.driver == 'beanstalkt':
            yield self.client.delete(event_id)
