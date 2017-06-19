"""
Persist Helper Module
"""
from __future__ import print_function

import json
import logging
import os

import psycopg2

from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


logger = logging.getLogger('eventify.persist')


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


def create_pg(database_name):
    """
    Create new postgres database
    :param database_name: Name of database to create
    """
    conn = connect_pg('postgres')
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute('CREATE DATABASE ' + database_name)
    cur.close()
    conn.close()


def create_pg_table(table_name):
    """
    Create table on event history
    :param table_name: The topic name
    """
    try:
        conn = connect_pg('event_history')
        cur = conn.cursor()
        query = """
            CREATE TABLE IF NOT EXISTS %s (
                id SERIAL PRIMARY KEY,
                event JSON NOT NULL,
                issued_at timestamp without time zone default (now() at time zone 'utc')
            )
        """ % table_name
        cur.execute(query)
        cur.close()
        conn.commit()
    except psycopg2.DatabaseError as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()


def persist_event(topic, event):
    """
    Track event to prevent duplication of work
    and potential loss of event
    :param topic: The event topic
    :param event: The event object
    """
    # Event to json
    json_event = event.as_json()

    # Create database if doesn't exist
    try:
        conn = connect_pg('event_history')
    except RuntimeError as error:
        create_pg('event_history')
        conn = connect_pg('event_history')

    # Create table if doesn't exist
    create_pg_table(topic)

    # Insert event if not processed
    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("SELECT id FROM {} WHERE event->>'event_id'=%s")
            .format(sql.Identifier(topic)),
            [event.event_id])
        exists = cur.fetchone()
        if exists:
            raise SystemError("Attempted to reissue same event")

        cur.execute(sql.SQL("INSERT INTO {} (event) VALUES (%s)")
            .format(sql.Identifier(topic)),
            [json_event])
        conn.commit()
        cur.close()
    except psycopg2.IntegrityError as error:
        logger.error(error)
