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

from eventify import logger
from eventify.stream import Stream


class ProducerHandler(tornado.web.RequestHandler):
    """
    Handles requests to a producer service

    Note:
        Inherits from tornado.web.RequestHandler
    """

    def initialize(self, host='localhost', topic='default', driver='beanstalkd'):
        """
        Setup producer

        Args:
            host (basestring): FQDN of queue system
            topic (basestring): Topic you want to publish to
            driver (basestring): Name of driver you want to use
        """
        self.host = host
        self.topic = topic
        self.driver = driver
        logger.debug('setup request handler with: %s %s %s' % (host, topic, driver))


    def post(self):
        """
        Sends message to stream
        """
        self.data = tornado.escape.json_decode(self.request.body)
        logger.debug('received request data: %s' % self.data)

        self.headers = self.request.headers
        logger.debug('received request headers: %s' % self.headers)

        self.validate_user_input()
        logger.debug('validated user input')

        future = self.producer()
        future.add_done_callback(done_callback)


    def write_error(self, status_code, **kwargs):
        """
        Use JSON instead of HTML
        for error resposne

        Args:
            status_code (int): HTTP status code

        Keyword Args:
            exc_info (HTTPError): sent from tornado
            message (basestring): sent from app
        """
        message = None
        if 'exc_info' in kwargs:
            message = str(kwargs['exc_info'][1])
        if 'message' in kwargs:
            message = str(kwargs['message'])

        self.set_status(status_code)
        self.set_header('Content-Type', 'application/json')
        self.write({
            'status_code': status_code,
            'message': message
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
                raise tornado.web.HTTPError(400)


    def log_exception(self, type, value, tb):
        """
        Log exceptions from async calls

        Args:
            type:
            value:
            tb: traceback
        """
        logger.debug(type, value)
        logger.debug(tb)


    def data_received(self, chunk):
        """
        Stream data

        Args:
            chunk:
        """
        logger.debug(chunk)

    @tornado.gen.coroutine
    def producer(self):
        """
        Connects to stream and sends message
        """
        logger.debug('emitting event')
        stream = Stream(host=self.host, topic=self.topic, driver=self.driver)
        stream.emit_event(self.data)
        logger.debug('event emitted!')


def done_callback(future):
    """
    Let tornado know were done
    """
    future.result()
    logger.debug('callback fired!')
