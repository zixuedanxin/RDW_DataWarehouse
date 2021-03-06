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

'''
Created on May 22, 2013

@author: ejen
'''
from __future__ import absolute_import
import datetime

from celery.utils.log import get_task_logger
from edudl2.udl2.celery import udl2_conf, celery
from edudl2.udl2 import message_keys as mk
from edudl2.udl2.udl2_base_task import Udl2BaseTask
from edudl2.move_to_integration.move_to_integration import move_data_from_staging_to_integration
from edudl2.udl2_util.measurement import BatchTableBenchmark
from edudl2.udl2.constants import Constants
from edudl2.udl2_util.util import merge_to_udl2stat_notification
from edudl2.udl2_util.exceptions import UDL2DataLoadingException

logger = get_task_logger(__name__)


@celery.task(name="udl2.W_load_to_integration_table.task", base=Udl2BaseTask)
def task(msg):
    start_time = datetime.datetime.now()
    logger.info("LOAD_FROM_STAGING_TO_INT: Migrating data from staging to integration.")
    guid_batch = msg[mk.GUID_BATCH]
    conf = generate_conf(guid_batch, msg[mk.LOAD_TYPE])
    success_rows, fail_rows = move_data_from_staging_to_integration(conf)
    end_time = datetime.datetime.now()

    notification_data = {mk.TOTAL_ROWS_LOADED: success_rows, mk.TOTAL_ROWS_NOT_LOADED: fail_rows}
    merge_to_udl2stat_notification(guid_batch, notification_data)
    if success_rows is 0:
        raise UDL2DataLoadingException()

    # benchmark
    benchmark = BatchTableBenchmark(guid_batch, msg[mk.LOAD_TYPE], task.name, start_time, end_time, size_records=success_rows,
                                    task_id=str(task.request.id), working_schema=conf[mk.TARGET_DB_SCHEMA], tenant=msg[mk.TENANT_NAME])
    benchmark.record_benchmark()

    # Outgoing message to be piped to the file expander
    outgoing_msg = {}
    outgoing_msg.update(msg)
    outgoing_msg.update({mk.PHASE: 4, mk.TOTAL_ROWS_LOADED: success_rows, mk.TOTAL_ROWS_NOT_LOADED: fail_rows})
    return outgoing_msg


def generate_conf(guid_batch, load_type):
    conf = {mk.GUID_BATCH: guid_batch,
            mk.SOURCE_DB_TABLE: Constants.UDL2_STAGING_TABLE(load_type),
            mk.TARGET_DB_SCHEMA: udl2_conf['udl2_db_conn']['db_schema'],
            mk.TARGET_DB_TABLE: Constants.UDL2_INTEGRATION_TABLE(load_type),
            mk.ERR_LIST_TABLE: Constants.UDL2_ERR_LIST_TABLE,
            mk.REF_TABLE: Constants.UDL2_REF_MAPPING_TABLE(load_type)}
    return conf
