"""
Produce Events From UI
"""
from datetime import datetime
import json
import os
import socket

import beanstalkt
import tornado.escape
import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web

class ProducerHandler(tornado.web.RequestHandler):
    """
    Handles requests from API Gateway
    :inherits RequestHandler:
    """

    def initialize(self):
        queue_host = os.getenv('QUEUE_HOST', 'localhost')
        self.client = beanstalkt.Client(host=queue_host)
        self.queue = os.getenv('QUEUE_NAME', "ui_events")


    def post(self):
        """
        Sends message to database and then streams to
        Beanstalk Queue
        """
        self.data = tornado.escape.json_decode(self.request.body)
        self.headers = self.request.headers
        self.validate_user_input()
        future = self.producer()
        future.add_done_callback(self.done_callback)


    def write_error(self, status_code, **kwargs):
        """
        Use JSON instead of HTML
        for error resposne
        :param status_code: HTTP status code
        """
        self.set_status(400)
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
        Send event to queue
        """
        # Convert data to bytes
        payload = str.encode(json.dumps(self.data))

        # Connect to beanstalkt
        yield self.client.connect()

        # Configure which queue to use
        yield self.client.use(self.queue)

        # Send the message
        yield self.client.put(payload)

        print(str(datetime.now()) + " " + "sent message")

    def done_callback(self, future):
        future.result()


def start_app():
    """
    Start listening for UI Events
    """
    app = tornado.web.Application([
        (r"/", ProducerHandler),
    ]).listen(8080)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    try:
        start_app()
    except KeyboardInterrupt:
        import sys
        sys.exit()
