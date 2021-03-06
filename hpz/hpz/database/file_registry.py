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

from datetime import datetime
import logging
from uuid import uuid4
from hpz.database.constants import HPZ
from hpz.database.hpz_connector import get_hpz_connection

__author__ = 'okrook'

logger = logging.getLogger(__name__)


class FileRegistry:

    @staticmethod
    def register_request(user_id, email):
        registration_id = uuid4()
        registration_info = {HPZ.REGISTRATION_ID: str(registration_id), HPZ.USER_ID: user_id, HPZ.EMAIL: email}

        with get_hpz_connection() as conn:
            file_reg_table = conn.get_table(table_name=HPZ.TABLE_NAME)
            conn.execute(file_reg_table.insert().values(registration_info))

        return registration_id

    @staticmethod
    def update_registration(registration_id, file_path, file_name):
        registration_info = {HPZ.FILE_PATH: file_path,
                             HPZ.CREATE_DT: datetime.now(),
                             HPZ.FILE_NAME: file_name}

        with get_hpz_connection() as conn:
            file_reg_table = conn.get_table(table_name=HPZ.TABLE_NAME)
            result = conn.execute(file_reg_table.update().where(file_reg_table.c.registration_id == registration_id).
                                  values(registration_info))

            return result.rowcount > 0

    @staticmethod
    def get_registration_info(registration_id):
        with get_hpz_connection() as conn:
            file_reg_table = conn.get_table(table_name=HPZ.TABLE_NAME)
            result = conn.execute(file_reg_table.select().where(file_reg_table.c.registration_id == registration_id))

            registration_info = result.fetchone()

            return registration_info

    @staticmethod
    def is_file_registered(registration_id):
        with get_hpz_connection() as conn:
            file_reg_table = conn.get_table(table_name=HPZ.TABLE_NAME)
            result = conn.execute(file_reg_table.select(limit=1).where(file_reg_table.c.registration_id == registration_id))

            return result.rowcount == 1
