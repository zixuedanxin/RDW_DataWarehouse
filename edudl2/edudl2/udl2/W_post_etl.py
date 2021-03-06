# (c) 2014 Amplify Education, Inc. All rights reserved, subject to the license
# below.
#
# Education agencies that are members of the Smarter Balanced Assessment
# Consortium as of August 1, 2014 are granted a worldwide, non-exclusive, fully
# paid-up, royalty-free, perpetual license, to access, use, execute, reproduce,
# display, distribute, perform and create derivative works of the software
# included in the Reporting Platform, including the source code to such software.
# This license includes the right to grant sublicenses by such consortium members
# to third party vendors solely for the purpose of performing services on behalf
# of such consortium member educational agencies.

from __future__ import absolute_import
from edudl2.udl2.celery import celery
from celery.utils.log import get_task_logger
import edudl2.udl2.message_keys as mk
from edudl2.udl2_util.measurement import BatchTableBenchmark
from edudl2.post_etl import post_etl
import datetime
from edudl2.udl2.udl2_base_task import Udl2BaseTask

logger = get_task_logger(__name__)


__author__ = 'sravi'

'''
Post ETL Worker for the UDL Pipeline.
The work zone files created as part of this run will be cleanedup.
The work zone directories created for this batch are available as part of the incoming_msg

The output of this worker will serve as the input to the subsequent worker [W_all_done].
'''


@celery.task(name="udl2.W_post_etl.task", base=Udl2BaseTask)
def task(incoming_msg):
    """
    Celery task that handles clean-up of files created during the UDL process.
    This task currently will clean up work zone to remove all the files that were generated as part of this batch
    @param incoming_msg: the message received from the penultimate step in the UDL process. Contains all params needed
    """
    start_time = datetime.datetime.now()
    guid_batch = incoming_msg.get(mk.GUID_BATCH)
    load_type = incoming_msg.get(mk.LOAD_TYPE)

    # do the cleanup
    post_etl.cleanup(incoming_msg)
    finish_time = datetime.datetime.now()

    # Benchmark
    benchmark = BatchTableBenchmark(guid_batch, load_type, task.name, start_time,
                                    finish_time, task_id=str(task.request.id), tenant=incoming_msg.get(mk.TENANT_NAME))
    benchmark.record_benchmark()

    # Outgoing message to be piped to All Done
    outgoing_msg = {}
    outgoing_msg.update(incoming_msg)
    return outgoing_msg
