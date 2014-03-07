__author__ = 'tshewchuk'

"""
This task provides jobs status notification to the client via an HTTP POST to a URL provided by the client.
It is meant to be executed after the UDL pipeline has completed.
"""

import datetime

from celery.utils.log import get_task_logger
from edudl2.udl2.udl2_base_task import Udl2BaseTask
from edudl2.udl2 import message_keys as mk
from edudl2.udl2.celery import celery, udl2_conf
from edudl2.udl2_util.measurement import BatchTableBenchmark
from edudl2.notification.notification import post_udl_job_status

logger = get_task_logger(__name__)


@celery.task(name='udl2.W_job_status_notification.task', base=Udl2BaseTask)
def task(msg):
    """
    This is the main function for the W_job_status_notification task.  It extracts the job callback URL
    provided by the client, and calls the method which sends the job status and any errors to the client.
    It then logs the status of the notification, and exits.
    """

    # Send the status.
    start_time = datetime.datetime.now()
    notification_status, notification_messages = post_udl_job_status(get_conf(msg))

    # Post the notification status and errors to the UDL_BATCH DB table.
    end_time = datetime.datetime.now()
    benchmark = BatchTableBenchmark(msg[mk.GUID_BATCH], msg[mk.LOAD_TYPE], 'UDL_JOB_STATUS_NOTIFICATION',
                                    start_time, end_time, udl_phase_step_status=notification_status,
                                    error_desc=notification_messages)
    benchmark.record_benchmark()

    return msg


def get_conf(msg):
    conf = {
        mk.CALLBACK_URL: msg[mk.CALLBACK_URL],
        mk.STUDENT_REG_GUID: msg[mk.STUDENT_REG_GUID],
        mk.REG_SYSTEM_ID: msg[mk.REG_SYSTEM_ID],
        mk.GUID_BATCH: msg[mk.GUID_BATCH],
        mk.BATCH_TABLE: udl2_conf['udl2_db'][mk.BATCH_TABLE],
        'retries': udl2_conf['sr_notification_retries'],
        'retry_interval': udl2_conf['sr_notification_retry_interval']
    }

    return conf
