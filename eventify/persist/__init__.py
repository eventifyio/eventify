"""
Persist Helper Module
"""
from __future__ import print_function

import json
import logging
import os

import psycopg2

from sqlalchemy import create_engine, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import OperationalError

from eventify.persist.constants import EVENT_DB_HOST, EVENT_DB_USER, EVENT_DB_PASS, \
                                       EVENT_DB_POOL_SIZE
from eventify.persist.models import get_table


logger = logging.getLogger('eventify.persist')


def connect_pg(database_name):
    """
    Connect to Postgres Server
    :param database_name: Name of database connecting to
    :return: Connection Ref
    """
    engine = create_engine(
        'postgresql+psycopg2://%s:%s@%s/%s' % (
            EVENT_DB_USER,
            EVENT_DB_PASS,
            EVENT_DB_HOST,
            database_name
        ),
        pool_size=EVENT_DB_POOL_SIZE,
        max_overflow=0,
        pool_recycle=3600,
        pool_timeout=10
    )
    return engine


def create_pg(database_name):
    """
    Create new postgres database
    :param database_name: Name of database to create
    """
    engine = connect_pg('postgres')
    conn = engine.connect()
    conn.execution_options(isolation_level="AUTOCOMMIT").execute('CREATE DATABASE ' + database_name)
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

    # Connect to database or create and connect if non existent
    engine = connect_pg('event_history')
    try:
        conn = engine.connect()
    except OperationalError as error:
        create_pg('event_history')
        conn = engine.connect()

    table = get_table(topic, engine)

    # Insert event if not processed
    try:
        select_stmt = select(table.c.event['event_id'].astext == event.event_id)
        results = conn.execute(select_stmt)
        exists = results.fetchone()
        if exists:
            raise SystemError("Attempted to reissue same event")

        insert_stmt = insert(table).values(event=json_event)
        conn.execute(insert_stmt)
    except psycopg2.IntegrityError as error:
        logger.error(error)
