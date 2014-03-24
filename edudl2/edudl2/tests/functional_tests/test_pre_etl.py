import unittest
from edudl2.udl2.defaults import UDL2_DEFAULT_CONFIG_PATH_FILE
from uuid import uuid4
import os
from edudl2.preetl.pre_etl import pre_etl_job
from edudl2.database.udl2_connector import initialize_db_udl, get_udl_connection
from edudl2.udl2_util.config_reader import read_ini_file
import tempfile
import shutil
from edudl2.exceptions.errorcodes import ErrorCode


class PreEtlTest(unittest.TestCase):

    def setUp(self):
        # get conf file
        config_path_file = UDL2_DEFAULT_CONFIG_PATH_FILE
        conf_tup = read_ini_file(config_path_file)
        self.udl2_conf = conf_tup[0]
        initialize_db_udl(self.udl2_conf)

        # create test error log file
        self.temp_dir = tempfile.mkdtemp()
        self.test_error_log_file = os.sep.join([self.temp_dir, 'test_error_log.log'])
        open(self.test_error_log_file, 'w').close()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_pre_etl_job(self):
        # read log file, should be empty
        self._check_log_file(is_empty=True)
        batch_guid_forced = str(uuid4())
        batch_guid = pre_etl_job(self.udl2_conf, log_file=self.test_error_log_file, batch_guid_forced=batch_guid_forced)
        self._check_log_file(is_empty=True)

        # make sure that the forced batch guid passed is same as the one pre_etc_job returns
        self.assertEqual(batch_guid_forced, batch_guid)

        # check one row is inserted in batch table
        with get_udl_connection() as conn:
            query = 'SELECT COUNT(*) from "{batch_table}" WHERE guid_batch = \'{batch_guid}\''.format(batch_guid=batch_guid,
                                                                                                      batch_table=self.udl2_conf['udl2_db']['batch_table'])
            result = conn.execute(query)
            num_of_row = 0
            for row in result:
                num_of_row = row[0]
                break
            self.assertEqual(str(num_of_row), '1')

            # delete this row
            delete_query = 'DELETE FROM "{batch_table}" WHERE guid_batch = \'{batch_guid}\''.format(batch_guid=batch_guid,
                                                                                                    batch_table=self.udl2_conf['udl2_db']['batch_table'])
            conn.execute(delete_query)

    def test_pre_etl_job_forced_guid(self):
        # read log file, should be empty
        self._check_log_file(is_empty=True)
        batch_guid = pre_etl_job(self.udl2_conf, log_file=self.test_error_log_file)
        self._check_log_file(is_empty=True)

        # check one row is inserted in batch table
        with get_udl_connection() as conn:
            query = 'SELECT COUNT(*) from "{batch_table}" WHERE guid_batch = \'{batch_guid}\''.format(batch_guid=batch_guid,
                                                                                                      batch_table=self.udl2_conf['udl2_db']['batch_table'])
            result = conn.execute(query)
            num_of_row = 0
            for row in result:
                num_of_row = row[0]
                break
            self.assertEqual(str(num_of_row), '1')

            # delete this row
            delete_query = 'DELETE FROM "{schema}"."{batch_table}" WHERE guid_batch = \'{batch_guid}\''.format(batch_guid=batch_guid,
                                                                                                               schema=self.udl2_conf['udl2_db']['db_schema'],
                                                                                                               batch_table=self.udl2_conf['udl2_db']['batch_table'])
            conn.execute(delete_query)

    def _check_log_file(self, is_empty):
        with open(self.test_error_log_file) as f:
            content = f.readlines()
        if is_empty is True:
            self.assertEqual(len(content), 0)
        else:
            self.assertTrue(len(content) > 0)
            expected_error_code = ErrorCode.BATCH_REC_FAILED

            # get error code in log message
            actual_error_code = content[0].split(']')[1].split(':')[0].strip()
            self.assertEqual(expected_error_code, actual_error_code)
