"""
Example Async Producer

curl -X POST localhost:8080 -d '{"event": "ClientRequested", "body": "im an event! 2", "company_id": 5, "app_id": 1, "global_tenant_id": "1234"}'
"""
import tornado.ioloop
import tornado.web

from eventify.producer import ProducerHandler


if __name__ == '__main__':
    try:
        port = 8080
        tornado.web.Application([
            (r"/", ProducerHandler, dict(config='producer-config.json')),
        ]).listen(port)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        # Clean ctrl+c
        import sys
        sys.exit()
