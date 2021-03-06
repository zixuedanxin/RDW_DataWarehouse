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

import logging
from edcore.notification.constants import Constants
from edcore.notification.callback import post_notification
from edcore.notification.mail import send_notification_email
from edcore.database.utils.constants import UdlStatsConstants, LoadType
import json
from edcore.database.utils.query import update_udl_stats_by_batch_guid
import time
import datetime

'''
This package contains the methods needed to post notification of the status, and any errors,
of the current completed UDL job to the job client.
'''

logger = logging.getLogger(__name__)


def send_notification(conf):
    '''
    Post the status and any errors of the current completed UDL job referenced by guid_batch
    to the client via callback_url

    :param conf: Notification task configuration

    :return: Notification status and any error messages
    '''
    email_notification_error = None
    notification_json = conf.get(UdlStatsConstants.NOTIFICATION)
    notification_conf = json.loads(notification_json if notification_json is not None else '{}')
    notification = notification_conf if notification_conf is not None and notification_conf else {}
    guid_batch = conf.get(UdlStatsConstants.BATCH_GUID)
    call_back = notification.get(Constants.CALLBACK_URL)
    emailnotification = notification_conf.get(Constants.EMAILNOTIFICATION)
    mail_server = conf.get(Constants.MAIL_SERVER)
    mail_sender = conf.get(Constants.MAIL_SENDER)
    load_status = conf.get(UdlStatsConstants.LOAD_STATUS)
    load_type = conf.get(UdlStatsConstants.LOAD_TYPE)
    if load_status is not None:
        notification_body = create_notification_body(load_type, guid_batch,
                                                     'udl_batch' if load_status.startswith('udl') else 'migrate',
                                                     notification.get(Constants.STUDENT_REG_GUID),
                                                     notification.get(Constants.REG_SYSTEM_ID),
                                                     notification.get(Constants.TOTAL_ROWS_LOADED, 0),
                                                     load_status,
                                                     notification.get(Constants.UDL_PHASE),
                                                     notification.get(Constants.ERROR_DESC),
                                                     notification.get('tsb_error'))

        notification_status = {}
        call_back_timestamp = ''
        email_timestamp = ''
        callback_notification_status = None
        callback_notification_error = None
        email_notification_error = None
        if call_back is not None:
            ts = time.time()
            call_back_timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            callback_notification_status, callback_notification_error = post_notification(call_back,
                                                                                          notification.get(Constants.NOTIFICATION_TIMEOUT_INTERVAL),
                                                                                          notification_body)
        notification_status['call_back'] = {'timestamp': call_back_timestamp, 'status': callback_notification_status, 'error': callback_notification_error}

        if emailnotification is not None:
            try:
                subject = 'Data Load - ' + notification_body['status'] + ' - Batch ' + guid_batch
                send_notification_email(mail_server, mail_sender, emailnotification, subject, notification_body)
                email_notification_error = Constants.SUCCESS
            except:
                email_notification_error = Constants.FAILURE
            ts = time.time()
            email_timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        notification_status['email'] = {'timestamp': email_timestamp, 'status': email_notification_error}
        update_udl_stats_by_batch_guid(guid_batch, {UdlStatsConstants.NOTIFICATION_STATUS: json.dumps(notification_status)})


def create_notification_body(load_type, guid_batch, batch_table, id, test_registration_id, row_count, udl_load_status, udl_phase, error_desc, tsb_error):
    '''
    Create the notification request body for the job referenced by guid_batch.

    :param guid_batch: Batch GUID of current job
    :param batch_table: Batch table name
    :param id: Student GUID
    :param test_registration_id: Test registration system ID
    :param row_count: totla rows loaded
    :param udl_phase_step_status: udl phase step status
    :param udl_phase: udl phase
    :param error_desc: error description

    :return: Notification request body
    '''

    status_codes = {UdlStatsConstants.MIGRATE_INGESTED: 'Success', UdlStatsConstants.UDL_STATUS_FAILED: 'Failed', UdlStatsConstants.MIGRATE_FAILED: 'Failed'}

    messages = []
    if udl_load_status == UdlStatsConstants.MIGRATE_INGESTED:
        messages.append('Job completed successfully')
    else:
        messages.append(error_desc if error_desc is not None else '')

    notification_body = {'status': status_codes[udl_load_status], 'message': messages}
    if load_type == LoadType.STUDENT_REGISTRATION:
        notification_body['id'] = id
    if test_registration_id is not None:
        notification_body['testRegistrationId'] = test_registration_id

    if udl_load_status == UdlStatsConstants.MIGRATE_INGESTED:
        notification_body['rowCount'] = row_count

    if tsb_error is not None:
        notification_body['tsb_error'] = tsb_error
    return notification_body
