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


class RecordProcessor(processor.RecordProcessorBase):
    """
    A RecordProcessor processes data from a shard in a stream. Its methods will be called with this pattern:
    * initialize will be called once
    * process_records will be called zero or more times
    * shutdown will be called if this MultiLangDaemon instance loses the lease to this shard, or the shard ends due
        a scaling change.
    """
    def __init__(self):
        self._SLEEP_SECONDS = 5
        self._CHECKPOINT_RETRIES = 5
        self._CHECKPOINT_FREQ_SECONDS = 60
        self._largest_seq = (None, None)
        self._largest_sub_seq = None
        self._last_checkpoint_time = None

    def initialize(self, initialize_input):
        """
        Called once by a KCLProcess before any calls to process_records
        :param amazon_kclpy.messages.InitializeInput initialize_input: Information about the lease that this record
            processor has been assigned.
        """
        self._largest_seq = (None, None)
        self._last_checkpoint_time = time.time()

    def checkpoint(self, checkpointer, sequence_number=None, sub_sequence_number=None):
        """
        Checkpoints with retries on retryable exceptions.
        :param amazon_kclpy.kcl.Checkpointer checkpointer: the checkpointer provided to either process_records
            or shutdown
        :param str or None sequence_number: the sequence number to checkpoint at.
        :param int or None sub_sequence_number: the sub sequence number to checkpoint at.
        """
        for n in range(0, self._CHECKPOINT_RETRIES):
            try:
                checkpointer.checkpoint(sequence_number, sub_sequence_number)
                return
            except kcl.CheckpointError as e:
                if 'ShutdownException' == e.value:
                    #
                    # A ShutdownException indicates that this record processor should be shutdown. This is due to
                    # some failover event, e.g. another MultiLangDaemon has taken the lease for this shard.
                    #
                    print('Encountered shutdown exception, skipping checkpoint')
                    return
                elif 'ThrottlingException' == e.value:
                    #
                    # A ThrottlingException indicates that one of our dependencies is is over burdened, e.g. too many
                    # dynamo writes. We will sleep temporarily to let it recover.
                    #
                    if self._CHECKPOINT_RETRIES - 1 == n:
                        sys.stderr.write('Failed to checkpoint after {n} attempts, giving up.\n'.format(n=n))
                        return
                    else:
                        print('Was throttled while checkpointing, will attempt again in {s} seconds'
                              .format(s=self._SLEEP_SECONDS))
                elif 'InvalidStateException' == e.value:
                    sys.stderr.write('MultiLangDaemon reported an invalid state while checkpointing.\n')
                else:  # Some other error
                    sys.stderr.write('Encountered an error while checkpointing, error was {e}.\n'.format(e=e))
            time.sleep(self._SLEEP_SECONDS)

    def process_record(self, data, partition_key, sequence_number, sub_sequence_number):
        """
        Called for each record that is passed to process_records.
        :param str data: The blob of data that was contained in the record.
        :param str partition_key: The key associated with this recod.
        :param int sequence_number: The sequence number associated with this record.
        :param int sub_sequence_number: the sub sequence number associated with this record.
        """
        ####################################
        # Insert your processing logic here
        ####################################
        return

    def should_update_sequence(self, sequence_number, sub_sequence_number):
        """
        Determines whether a new larger sequence number is available
        :param int sequence_number: the sequence number from the current record
        :param int sub_sequence_number: the sub sequence number from the current record
        :return boolean: true if the largest sequence should be updated, false otherwise
        """
        return self._largest_seq == (None, None) or sequence_number > self._largest_seq[0] or \
            (sequence_number == self._largest_seq[0] and sub_sequence_number > self._largest_seq[1])

    def process_records(self, process_records_input):
        """
        Called by a KCLProcess with a list of records to be processed and a checkpointer which accepts sequence numbers
        from the records to indicate where in the stream to checkpoint.
        :param amazon_kclpy.messages.ProcessRecordsInput process_records_input: the records, and metadata about the
            records.
        """
        try:
            for record in process_records_input.records:
                data = record.binary_data
                seq = int(record.sequence_number)
                sub_seq = record.sub_sequence_number
                key = record.partition_key
                self.process_record(data, key, seq, sub_seq)
                if self.should_update_sequence(seq, sub_seq):
                    self._largest_seq = (seq, sub_seq)

            #
            # Checkpoints every self._CHECKPOINT_FREQ_SECONDS seconds
            #
            if time.time() - self._last_checkpoint_time > self._CHECKPOINT_FREQ_SECONDS:
                self.checkpoint(process_records_input.checkpointer, str(self._largest_seq[0]), self._largest_seq[1])
                self._last_checkpoint_time = time.time()

        except Exception as e:
            sys.stderr.write("Encountered an exception while processing records. Exception was {e}\n".format(e=e))

    def shutdown(self, shutdown_input):
        """
        Called by a KCLProcess instance to indicate that this record processor should shutdown. After this is called,
        there will be no more calls to any other methods of this record processor.
        As part of the shutdown process you must inspect :attr:`amazon_kclpy.messages.ShutdownInput.reason` to
        determine the steps to take.
            * Shutdown Reason ZOMBIE:
                **ATTEMPTING TO CHECKPOINT ONCE A LEASE IS LOST WILL FAIL**
                A record processor will be shutdown if it loses its lease.  In this case the KCL will terminate the
                record processor.  It is not possible to checkpoint once a record processor has lost its lease.
            * Shutdown Reason TERMINATE:
                **THE RECORD PROCESSOR MUST CHECKPOINT OR THE KCL WILL BE UNABLE TO PROGRESS**
                A record processor will be shutdown once it reaches the end of a shard.  A shard ending indicates that
                it has been either split into multiple shards or merged with another shard.  To begin processing the new
                shard(s) it's required that a final checkpoint occurs.
        :param amazon_kclpy.messages.ShutdownInput shutdown_input: Information related to the shutdown request
        """
        try:
            if shutdown_input.reason == 'TERMINATE':
                # Checkpointing with no parameter will checkpoint at the
                # largest sequence number reached by this processor on this
                # shard id
                print('Was told to terminate, will attempt to checkpoint.')
                self.checkpoint(shutdown_input.checkpointer, None)
            else: # reason == 'ZOMBIE'
                print('Shutting down due to failover. Will not checkpoint.')
        except:
            pass


class EventProcessor(RecordProcessor):
    """
    Uses KCL to stream records from Kinesis
    http://docs.aws.amazon.com/streams/latest/dev/developing-consumers-with-kcl.html#kinesis-record-processor-overview-kcl
    """

    def process_record(self, data, partition_key, sequence_number):
        """
        Process Record
        """
        self.data = data
        self.handle_event()

    def handle_event(self):
        print(self.data)


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
        :param shard_count: Configure shard count
        """
        # Setup Defaults
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


    def listen(self):
        """
        Start listening for commands an events on stream from KCL
        """
        listener = kcl.KCLProcess(EventProcessor())
        listener.run()

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
