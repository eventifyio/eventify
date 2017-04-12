"""
Produce Events From UI
"""
from datetime import datetime
import json
import os
import socket

import tornado.escape
import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web

from eventify.stream import Stream


class ProducerHandler(tornado.web.RequestHandler):
    """
    Handles requests to a producer service

    Note:
        Inherits from tornado.web.RequestHandler
    """

    def post(self):
        """
        Sends message to stream
        """
        self.data = tornado.escape.json_decode(self.request.body)
        self.headers = self.request.headers
        self.reason = 'Unknown reason'

        self.validate_user_input()
        future = self.producer()
        future.add_done_callback(done_callback)


    def write_error(self, status_code, **kwargs):
        """
        Use JSON instead of HTML
        for error resposne

        Args:
            status_code (int): HTTP status code
        """
        self.set_status(status_code)
        self.set_header('Content-Type', 'application/json')
        self.write({
            'status_code': status_code,
            'reason': self.reason
        })
        self.finish()


    def validate_user_input(self):
        """
        Validates that all the input received is the
        expected input

        Subclass this function for your own validation needs
        """
        minimum_required_input = ['company_id', 'event', 'body', 'global_tenant_id', 'app_id']
        input_received = self.data.keys()
        for param in minimum_required_input:
            if param not in input_received:
                self.reason = "Missing required param '%s'" % param
                raise tornado.web.HTTPError(400)


    @tornado.gen.coroutine
    def producer(self):
        """
        Connects to stream and sends message
        """
        stream = Stream(topic="default")
        stream.emit_event(self.data)


def done_callback(future):
    """
    Let tornado know were done
    """
    future.result()


def start():
    """
    Start listening for UI Events
    """
    tornado.web.Application([
        (r"/", ProducerHandler),
    ]).listen(80)
    tornado.ioloop.IOLoop.current().start()
