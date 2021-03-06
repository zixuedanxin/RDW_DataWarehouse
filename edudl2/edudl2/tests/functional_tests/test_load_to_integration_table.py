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
Created on May 24, 2013

@author: ejen
'''
import os
from edudl2.move_to_integration.move_to_integration import move_data_from_staging_to_integration
from edudl2.fileloader.file_loader import load_file
from edudl2.udl2 import message_keys as mk
import edudl2.rule_maker.rules.code_generator_special_rules as sr
from edudl2.tests.functional_tests.util import UDLTestHelper
from edudl2.database.udl2_connector import get_udl_connection, initialize_db_udl
from edudl2.move_to_integration.move_to_integration import get_column_mapping_from_stg_to_int
from edudl2.udl2_util.database_util import get_db_connection_params
from edudl2.udl2.constants import Constants
from sqlalchemy.sql.expression import update
from uuid import uuid4
from nose.tools import nottest


class FuncTestLoadToIntegrationTable(UDLTestHelper):

    @classmethod
    def setUpClass(cls):
        super(FuncTestLoadToIntegrationTable, cls).setUpClass()
        initialize_db_udl(cls.udl2_conf)

    def load_file_to_stage(self, data_file, header_file, load_type, staging_table, guid):
        # file contain 30 rows
        conf = {
            mk.FILE_TO_LOAD: os.path.join(self.data_dir, data_file),
            mk.HEADERS: os.path.join(self.data_dir, header_file),
            mk.CSV_TABLE: 'csv_table_for_file_loader',
            mk.CSV_SCHEMA: self.udl2_conf['udl2_db_conn']['db_schema'],
            mk.REF_TABLE: Constants.UDL2_REF_MAPPING_TABLE(load_type),
            mk.CSV_LZ_TABLE: Constants.UDL2_CSV_LZ_TABLE,
            mk.FDW_SERVER: 'udl2_fdw_server',
            mk.TARGET_DB_SCHEMA: self.udl2_conf['udl2_db_conn']['db_schema'],
            mk.TARGET_DB_TABLE: staging_table,
            mk.APPLY_RULES: False,
            mk.ROW_START: 10,
            mk.GUID_BATCH: guid,
            mk.TENANT_NAME: 'cat'
        }
        load_file(conf)
        with get_udl_connection() as conn:
            _table = conn.get_table(staging_table)
            update_stmt = update(_table).values(record_sid=1000 + _table.c.src_file_rec_num - 1).\
                where(_table.c.guid_batch == guid)
            conn.execute(update_stmt)

    def postloading_count(self, table='int_sbac_asmt_outcome'):
        sql_template = """
            SELECT COUNT(*) FROM "{staging_schema}"."{staging_table}"
            WHERE guid_batch = '{guid_batch}'
        """
        with get_udl_connection() as conn:
            sql = sql_template.format(staging_schema=self.udl2_conf['udl2_db_conn']['db_schema'],
                                      staging_table=table,
                                      guid_batch=self.udl2_conf['guid_batch'])
            result = conn.execute(sql)
            count = 0
            for row in result:
                count = row[0]
            return count

    def generate_conf_for_moving_from_stg_to_int(self, guid_batch, load_type):
        db_params_tuple = get_db_connection_params(self.udl2_conf['udl2_db_conn']['url'])
        conf = {
            mk.GUID_BATCH: guid_batch,

            # source database setting
            mk.SOURCE_DB_DRIVER: db_params_tuple[0],
            mk.SOURCE_DB_USER: db_params_tuple[1],
            mk.SOURCE_DB_PASSWORD: db_params_tuple[2],
            mk.SOURCE_DB_HOST: db_params_tuple[3],
            mk.SOURCE_DB_PORT: db_params_tuple[4],
            mk.SOURCE_DB_NAME: db_params_tuple[5],
            mk.SOURCE_DB_SCHEMA: self.udl2_conf['udl2_db_conn']['db_schema'],
            mk.SOURCE_DB_TABLE: Constants.UDL2_STAGING_TABLE(load_type),

            # target database setting
            mk.TARGET_DB_SCHEMA: self.udl2_conf['udl2_db_conn']['db_schema'],
            mk.TARGET_DB_TABLE: Constants.UDL2_INTEGRATION_TABLE(load_type),

            mk.REF_TABLE: Constants.UDL2_REF_MAPPING_TABLE(load_type),
            mk.ERROR_DB_SCHEMA: self.udl2_conf['udl2_db_conn']['db_schema'],
            mk.ERR_LIST_TABLE: Constants.UDL2_ERR_LIST_TABLE
        }
        return conf

    def test_load_stage_to_int_assessment(self):
        '''
        functional tests for testing load from staging to integration as an independent unit tests.
        Use a fixed UUID for the moment. may be dynamic later.

        it loads 30 records from test csv file to stagint table then move it to integration.
        '''
        conf = self.generate_conf_for_moving_from_stg_to_int('00000000-0000-0000-0000-000000000000', 'assessment')
        self.udl2_conf['guid_batch'] = '00000000-0000-0000-0000-000000000000'
        self.load_file_to_stage('test_file_realdata.csv', 'test_file_headers.csv', 'assessment', 'stg_sbac_asmt_outcome', '00000000-0000-0000-0000-000000000000')
        move_data_from_staging_to_integration(conf)
        postloading_total = self.postloading_count()
        self.assertEqual(30, postloading_total)

        int_asmt_avgs = self.get_integration_asmt_score_avgs()
        stg_asmt_avgs = self.get_staging_asmt_score_avgs()

        self.assertEqual(stg_asmt_avgs, int_asmt_avgs)

        stg_demo_dict = self.get_staging_demographic_counts()
        int_demo_dict = self.get_integration_demographic_counts()

        derived_count = int_demo_dict.pop('dmg_eth_derived', None)
        self.assertIsNotNone(derived_count)
        self.assertEqual(stg_demo_dict, int_demo_dict)

    def test_load_stage_to_int_student_registration(self):
        guid_batch = str(uuid4())
        load_type = Constants.LOAD_TYPE_STUDENT_REGISTRATION
        conf = self.generate_conf_for_moving_from_stg_to_int(guid_batch, load_type)
        self.udl2_conf['guid_batch'] = guid_batch
        self.load_file_to_stage(os.path.join('student_registration_data', 'test_stu_reg_without_headers.csv'),
                                os.path.join('student_registration_data', 'test_stu_reg_header.csv'),
                                load_type, Constants.UDL2_STAGING_TABLE(load_type), guid_batch)
        move_data_from_staging_to_integration(conf)
        postloading_total = self.postloading_count(Constants.UDL2_INTEGRATION_TABLE(load_type))
        self.assertEqual(10, postloading_total)

    # not used in ref_table_data.py anymore
    @nottest
    def test_derive_eth_function(self):
        function_name = sr.special_rules['deriveEthnicity'][0]
        # dmg_eth_blk, dmg_eth_asn, dmg_eth_hsp, dmg_eth_ami, dmg_eth_pcf, dmg_eth_wht
        prepare_data = {'exception': {'src_column': "'sda', 'dg', 'a', 'q', 't', 'fff', 'z'", 'expected_code': -1},
                        'not stated 1': {'src_column': "NULL, NULL, NULL, NULL, NULL, NULL, NULL", 'expected_code': 0},
                        'not stated 2': {'src_column': "'f', NULL, NULL, 'f', NULL, 'f', NULL", 'expected_code': 0},
                        'african american': {'src_column': "'y', 'n', 'n', 'n', 'n', 'n', 'n'", 'expected_code': 1},
                        'asian': {'src_column': "'n', 'y', 'n', 'n', 'n', 'n', 'n'", 'expected_code': 2},
                        'hispanic 1': {'src_column': "'n', 'n', 'y', 'n', 'n', 'n', 'n'", 'expected_code': 3},
                        'hispanic 2': {'src_column': "'n', 'n', 'y', 'y', 'n', 'y', 'n'", 'expected_code': 3},
                        'hispanic 3': {'src_column': "'n', 'n', 'y', 'n', 'n', 'n', 'y'", 'expected_code': 3},
                        'native american': {'src_column': "'n', 'n', 'n', 'y', 'n', 'n', 'n'", 'expected_code': 4},
                        'pacific islander': {'src_column': "'n', 'n', 'n', 'n', 'y', 'n', 'n'", 'expected_code': 5},
                        'white': {'src_column': "'n', 'n', 'n', 'n', 'n', 'y', 'n'", 'expected_code': 6},
                        'two or more races 1': {'src_column': "'y', 'n', 'n', 'n', 'n', 'y', 'n'", 'expected_code': 1},
                        'two or more races 2': {'src_column': "'n', 'y', 'n', 'n', NULL, 'y', 'n'", 'expected_code': 2},
                        'two or more races 3': {'src_column': "'y', 'y', 'n', 'y', 'y', 'y', 'y'", 'expected_code': 7},
                        'two or more races 4': {'src_column': "'n', 'n', 'n', 'n', 'n', 'n', 'y'", 'expected_code': 7}
                        }
        sql_template = 'SELECT %s;' % function_name
        with get_udl_connection() as conn:
            for _key, value in prepare_data.items():
                sql = sql_template.format(src_column=value['src_column'])
                result = conn.execute(sql)
                actual_value = ''
                for r in result:
                    actual_value = r[0]
                    break
                self.assertEqual(actual_value, value['expected_code'])

    def test_get_column_mapping_from_stg_to_int(self):
        expected_target_columns = ['name_state', 'code_state', 'guid_district', 'name_district', 'guid_school', 'name_school',
                                   'guid_student', 'external_ssid_student', 'name_student_first', 'name_student_middle', 'name_student_last',
                                   'birthdate_student', 'sex_student', 'grade_enrolled', 'dmg_eth_hsp', 'dmg_eth_ami', 'dmg_eth_asn',
                                   'dmg_eth_blk', 'dmg_eth_pcf', 'dmg_eth_wht', 'dmg_multi_race', 'dmg_prg_iep', 'dmg_prg_lep', 'dmg_prg_504', 'dmg_sts_ecd',
                                   'dmg_sts_mig', 'code_language', 'eng_prof_lvl', 'us_school_entry_date', 'lep_entry_date',
                                   'lep_exit_date', 't3_program_type', 'prim_disability_type', 'created_date', 'guid_batch']
        expected_source_columns_with_tran_rule = ['substr("A".name_state, 1, 50)', 'substr("A".code_state, 1, 2)', 'substr("A".guid_district, 1, 40)',
                                                  'substr("A".name_district, 1, 60)', 'substr("A".guid_school, 1, 40)', 'substr("A".name_school, 1, 60)',
                                                  'substr("A".guid_student, 1, 40)', 'substr("A".external_ssid_student, 1, 40)', 'substr("A".name_student_first, 1, 35)',
                                                  'substr("A".name_student_middle, 1, 35)', 'substr("A".name_student_last, 1, 35)', 'substr("A".birthdate_student, 1, 10)',
                                                  'substr("A".sex_student, 1, 10)', 'substr("A".grade_enrolled, 1, 2)',
                                                  'case "A".dmg_eth_hsp when \'\' then null else cast("A".dmg_eth_hsp as bool) end',
                                                  'case "A".dmg_eth_ami when \'\' then null else cast("A".dmg_eth_ami as bool) end',
                                                  'case "A".dmg_eth_asn when \'\' then null else cast("A".dmg_eth_asn as bool) end',
                                                  'case "A".dmg_eth_blk when \'\' then null else cast("A".dmg_eth_blk as bool) end',
                                                  'case "A".dmg_eth_pcf when \'\' then null else cast("A".dmg_eth_pcf as bool) end',
                                                  'case "A".dmg_eth_wht when \'\' then null else cast("A".dmg_eth_wht as bool) end',
                                                  'case "A".dmg_multi_race when \'\' then null else cast("A".dmg_multi_race as bool) end',
                                                  'case "A".dmg_prg_iep when \'\' then null else cast("A".dmg_prg_iep as bool) end',
                                                  'case "A".dmg_prg_lep when \'\' then null else cast("A".dmg_prg_lep as bool) end',
                                                  'case "A".dmg_prg_504 when \'\' then null else cast("A".dmg_prg_504 as bool) end',
                                                  'case "A".dmg_sts_ecd when \'\' then null else cast("A".dmg_sts_ecd as bool) end',
                                                  'case "A".dmg_sts_mig when \'\' then null else cast("A".dmg_sts_mig as bool) end',
                                                  'substr("A".code_language, 1, 3)', 'substr("A".eng_prof_lvl, 1, 20)', 'substr("A".us_school_entry_date, 1, 10)',
                                                  'substr("A".lep_entry_date, 1, 10)', 'substr("A".lep_exit_date, 1, 10)', 'substr("A".t3_program_type, 1, 27)',
                                                  'substr("A".prim_disability_type, 1, 3)', '"A".created_date', '"A".guid_batch']
        with get_udl_connection() as conn:
            target_columns, source_columns_with_tran_rule = get_column_mapping_from_stg_to_int(conn,
                                                                                               Constants.UDL2_REF_MAPPING_TABLE(Constants.LOAD_TYPE_STUDENT_REGISTRATION),
                                                                                               'stg_sbac_stu_reg', 'int_sbac_stu_reg')
            self.assertEqual(expected_target_columns, target_columns)
            self.assertEqual(expected_source_columns_with_tran_rule, source_columns_with_tran_rule)
