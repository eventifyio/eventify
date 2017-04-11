"""
Consumer for UI Events
"""
from datetime import datetime
import json
import os
import socket

import beanstalkt
import tornado.gen
import tornado.ioloop


queue_host = os.getenv('QUEUE_HOST', 'localhost')
client = beanstalkt.Client(host=queue_host)
queue = os.getenv('QUEUE_NAME', "ui_events")

@tornado.gen.coroutine
def consumer():
    # Connect to Queue
    yield client.connect()
    yield client.use(queue)
    yield client.watch(queue)

    while True:
        job = yield client.reserve(timeout=0)
        try:
            if 'id' in job:
                job_id = job.get('id')
                if process_job(job):
                    yield client.delete(job_id)
        except TypeError as error:
            pass


@tornado.gen.coroutine
def process_job(job):
    """
    Process the job
    Since this is the UI Events consumer
    It is just going to write these events to a persistent datastore
    :param job: The raw message in bytes
    :return: Boolean
    """
    job_body = job.get('body').decode()
    message = json.loads(job_body)
    if persist_event(message):
        return True
    return False


def persist_event(message):
    """
    Connect to persistent store and store the
    event
    :param message: Dict
    :return: Boolean
    """
    print(str(datetime.now()) + " " + str(message))


def done_callback(future):
    future.result()


if __name__ == '__main__':
    try:
        future = consumer()
        future.add_done_callback(done_callback)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        import sys
        sys.exit()
