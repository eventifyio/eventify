"""
All Business Logic of a Service Lives Here
"""
import datetime

import tornado.gen

from eventify.stream import Stream


class EventHandler(Stream):
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
        events_to_process = self.events_to_process
        if event_name in events_to_process:
            method_to_call = getattr(EventHandler, events_to_process[event_name])
            if method_to_call(message):
                self.delete_event(event_id)


    @tornado.gen.coroutine
    def provision_node(self, message):
        """
        Pseudo func

        Args:
            message (json): Message
        """
        print('NodeProvisioned')


    #@tornado.gen.coroutine
    def start_node(message):
        """
        Pseudo func

        Args:
            message(json): Message
        """
        print('%s NodeStarted' % str(datetime.datetime.now()))
        return True
