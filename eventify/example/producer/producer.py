"""
Example Async Producer
"""
import tornado.ioloop
import tornado.web

from eventify.producer import ProducerHandler


if __name__ == '__main__':
    try:
        # Setup Producer
        host = 'localhost'
        topic = 'dev'
        port = 8080

        # Start app
        tornado.web.Application([
            (r"/", ProducerHandler, dict(host=host, topic=topic)),
        ]).listen(port)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        # Clean ctrl+c
        import sys
        sys.exit()
