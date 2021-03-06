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
Created on Oct 9, 2014

@author: tosako
'''
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPOk, HTTPServerError
from hpz.database.hpz_connector import get_hpz_connection
from sqlalchemy.sql.expression import select
import os
import uuid
import logging


logger = logging.getLogger('hpz')
HEARTBAET_FILE_SIZE = 1024


@view_config(route_name='heartbeat', permission=NO_PERMISSION_REQUIRED, request_method='GET')
def heartbeat(request):
    '''
    service end point for heartbeat
    '''
    base_upload_path = request.registry.settings['hpz.frs.upload_base_path']
    if check_database() and check_file_write(base_upload_path):
        return HTTPOk()
    return HTTPServerError()


def check_database():
    '''
    check database connection
    '''
    database_ok = False
    try:
        with get_hpz_connection() as conn:
            query = select([1])
            results = conn.get_result(query)
            if len(results) > 0:
                database_ok = True
    except Exception as e:
        logger.error('HPZ Heartbeat failed. Check DB connection.' + str(e))
        pass
    return database_ok


def check_file_write(base_upload_path):
    '''
    check file wirtable
    :param base_upload_path: uplaod base path
    '''
    file_ok = False
    file_id = uuid.uuid4()
    heartbeat_file_path = os.path.join(base_upload_path, '.heartbeat-' + str(file_id))
    try:
        with open(heartbeat_file_path, 'w') as f:
            f.write('0' * HEARTBAET_FILE_SIZE)
        fstat = os.stat(heartbeat_file_path)
        if fstat.st_size == HEARTBAET_FILE_SIZE:
            file_ok = True
    except Exception as e:
        logger.error('HPZ Heartbeat failed at file write. %s', str(e))
        pass
    finally:
        if os.path.exists(heartbeat_file_path):
            os.remove(heartbeat_file_path)
    return file_ok
