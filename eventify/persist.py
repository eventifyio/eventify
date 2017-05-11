"""
Persist Helper Module
"""
from __future__ import print_function

import json
import os

import psycopg2

def connect_pg(database_name):
    """
    Connect to Postgres Server
    :param database_name: Name of database connecting to
    :return: Connection Ref
    """
    pg_host = os.getenv('PG_HOST', 'localhost')
    pg_user = os.getenv('PG_USER', 'dev')
    pg_pass = os.getenv('PG_PASS', 'test1234')
    try:
        return psycopg2.connect(
            dbname=database_name,
            user=pg_user,
            host=pg_host,
            password=pg_pass,
        )
    except psycopg2.OperationalError as error:
        raise RuntimeError("Unable to persist event! %s" % error)

def persist_event(event_id, event, message, state='in-flight'):
    """
    Track event to prevent duplication of work
    and potential loss of event
    :param event_id: Event Id
    :param event: The event object
    :param message: Body of event
    :param state: The state of event
    """
    conn = connect_pg('cloud_compute')

    try:
        cur = conn.cursor()
        query = "INSERT INTO message_tracking (id, event, message, state) VALUES (%s, %s, %s, %s)"
        cur.execute(query, (event_id, event, json.dumps(message), state))
        conn.commit()
        cur.close()
    except psycopg2.IntegrityError:
        raise RuntimeError("Work already in progress!")
