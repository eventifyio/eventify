"""
Eventify!
A simple module for implementing event driven systems
"""
import logging
import os

from botocore.exceptions import ClientError
from boto3 import Session


class Eventify(object):
    """
    Base Class for eventify
    """
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)


    def __init__(self, aws_access_key_id, aws_secret_access_key, stream_name, **kwargs):
        """
        :param aws_access_key_id: AWS Access Key
        :param aws_secret_access_key: AWS Secret Key
        :param stream_name: Kinesis Stream Name
        :param region_name: AWS Region Name
        :param record_limit: Max records to return for stream
        :param iterator_type:
            'AT_SEQUENCE_NUMBER'|'AFTER_SEQUENCE_NUMBER'|
            'TRIM_HORIZON'|'LATEST'|'AT_TIMESTAMP'
        :param shard_count: Configure shard count
        """
        # Setup Defaults
        self.record_limit = kwargs.get('record_limit', 10)
        self.iterator_type = kwargs.get('iterator_type', 'AFTER_SEQUENCE_NUMBER')
        self.shard_count = kwargs.get('shard_count', 1)

        # Setup AWS Session
        region_name = kwargs.get('region_name', 'us-east-1')
        session = Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

        # Setup Kinesis
        self.client = session.client('kinesis')
        self.stream_name = stream_name
        self.shard_id = None
        self.sequence_number = None


    def send_message(self, message):
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


    def get_current_location_in_stream(self, retry=None):
        """
        Get current current location in stream based on starting
        sequence number
        :param retry: Determine how many times we have tried since
        """
        if retry > 3:
            raise RuntimeError("Unable to determing current location in stream")

        try:
            response = self.client.get_shard_iterator(
                StreamName=self.stream_name,
                ShardId=self.shard_id,
                ShardIteratorType=self.iterator_type,
                StartingSequenceNumber=self.sequence_number
            )
            shard_iterator = response.get('ShardIterator', None)
            if shard_iterator is None:
                if retry is None:
                    retry = 1
                else:
                    retry += 1
                self.get_last_record()
                self.get_current_location_in_stream(retry)
            return shard_iterator
        except ClientError as err:
            raise RuntimeError(err)


    def get_last_record(self):
        """
        Get last record processed on stream
        """
        self.shard_id = 'shardId-000000000000'
        self.sequence_number = '49571983678701993825638767801390853477682321505828995074'


    def get_commands(self):
        """
        Get list of records from Kinesis
        """
        current_location = self.get_current_location_in_stream()
        try:
            response = self.client.get_records(
                ShardIterator=current_location,
                Limit=self.record_limit
            )
            records = response.get('Records', [])
            return records
        except ClientError as err:
            raise RuntimeError(err)


    def create_topic(self):
        """
        Create stream on kinesis
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
