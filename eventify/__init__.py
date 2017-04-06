"""
Eventify!
A simple module for implementing event driven systems
"""
from __future__ import print_function

import logging
import os
import sys
import time

from amazon_kclpy import kcl
from amazon_kclpy.v2 import processor
from botocore.exceptions import ClientError
from boto3 import Session

from eventify.drivers.kinesis.stream import EventProcessor


class Eventify(object):
    """
    Base Class for eventify
    """
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)


    def __init__(self, driver, **kwargs):
        """
        :param driver: Driver you wish to use
        :param kwargs: Driver settings
        """
        if driver == "kinesis":
            self.init_kinesis(**kwargs)
        else:
            raise ValueError("Driver not supported: %s" % self.driver)


    def init_kinesis(self, **kwargs):
        """
        :param aws_access_key_id: AWS Access Key
        :param aws_secret_access_key: AWS Secret Key
        :param stream_name: Kinesis Stream Name
        :param region_name: AWS Region Name
        :param shard_count: Configure shard count
        """
        # Setup Defaults
        self.shard_count = kwargs.get('shard_count', 1)

        # Setup AWS Session
        region_name = kwargs.get('region_name', 'us-east-1')
        aws_access_key_id = kwargs.get('aws_access_key_id', os.getenv('AWS_ACCESS_KEY_ID'))
        aws_secret_access_key = kwargs.get('aws_secret_access_key', os.getenv('AWS_SECRET_ACCESS_KEY'))
        session = Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

        # Setup Kinesis
        self.client = session.client('kinesis')
        self.stream_name = kwargs.get('stream_name', None)


    def listen(self):
        """
        Start listening for commands an events on stream from KCL
        """
        listener = kcl.KCLProcess(EventProcessor())
        listener.run()


    def emit_event(self, message):
        """
        Send a record to Kinesis Stream
        :param message: JSON Message to send to stream
        """
        try:
            response = self.client.put_record(
                StreamName=self.stream_name,
                Data=message,
                PartitionKey=self.stream_name
            )
            shard_id = response.get('ShardId', None)
            sequence_number = response.get('SequenceNumber', None)

            if shard_id is None:
                raise ValueError("Did not receive shard id from Kinesis!")
            if sequence_number is None:
                raise ValueError("Did not receive sequence_number from Kinesis!")

            self.shard_id = shard_id
            self.sequence_number = sequence_number
        except ClientError as err:
            raise RuntimeError(err)


    def register_topic(self):
        """
        Register stream on kinesis
        """
        try:
            return self.client.create_stream(
                StreamName=self.stream_name,
                ShardCount=self.shard_count
            )
        except ClientError as err:
            # log message but do not block most cases are:
            # topic already exists
            self.logger.error(err)


    def delete_topic(self):
        """
        Delete stream on kinesis
        """
        try:
            return self.client.delete_stream(
                StreamName=self.stream_name
            )
        except ClientError as err:
            raise RuntimeError(err)
