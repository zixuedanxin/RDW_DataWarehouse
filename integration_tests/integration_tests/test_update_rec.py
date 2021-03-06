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
Created on Apr 8, 2014

@author: bpatel
'''
import unittest
from integration_tests.udl_helper import empty_batch_table, empty_stats_table, run_udl_pipeline, migrate_data
import os
import shutil
import time
from uuid import uuid4
from edudl2.database.udl2_connector import get_prod_connection,\
    initialize_all_db
from edcore.database.stats_connector import StatsDBConnection
from sqlalchemy.sql import select, and_
from edudl2.udl2.celery import udl2_conf, udl2_flat_conf
from integration_tests import IntegrationTestCase


class Test(IntegrationTestCase):

    def setUp(self):
        self.tenant_dir = '/opt/edware/zones/landing/arrivals/cat/cat_user/filedrop'
        self.archived_file = self.require_gpg_file('test_update_record')
        initialize_all_db(udl2_conf, udl2_flat_conf)
        empty_stats_table(self)
        empty_batch_table(self)
        self.guid_batch_id = str(uuid4())
        self.tenant = 'cat'

    def tearDown(self):
        if os.path.exists(self.tenant_dir):
            shutil.rmtree(self.tenant_dir)

    def test_update_record(self):
        run_udl_pipeline(self, self.guid_batch_id)
        print("UDL pipeleine completed successfull")
        self.validate_edware_stats_table_before_mig()
        migrate_data(self)
        time.sleep(10)
        self.validate_edware_stats_table_after_mig()
        self.validate_edware_prod()

    def validate_edware_stats_table_before_mig(self):
        with StatsDBConnection() as conn:
            print()
            table = conn.get_table('udl_stats')
            query = select([table.c.load_status])
            result = conn.execute(query).fetchall()
            expected_result = [('udl.ingested',)]
            self.assertEquals(result, expected_result)

    # Validate udl_stats table under edware_stats DB for successful migration
    def validate_edware_stats_table_after_mig(self):
        with StatsDBConnection() as conn:
            table = conn.get_table('udl_stats')
            query = select([table.c.load_status])
            result = conn.execute(query).fetchall()
            expected_result = [('migrate.ingested',)]
            self.assertEquals(result, expected_result)

    def validate_edware_prod(self):
        with get_prod_connection(self.tenant) as connection:
            fact_table = connection.get_table('fact_asmt_outcome_vw')
            dim_student = connection.get_table('dim_student')
            update_output_data = select([fact_table.c.rec_status], and_(fact_table.c.student_id == 'f7251065-ca82-4248-9397-cc722e97bbdc', fact_table.c.asmt_guid == 'a685f0ec-a0a6-4b1e-93b8-0c4298ff6374'))
            update_output_table = connection.execute(update_output_data).fetchall()
            self.assertIn(('D',), update_output_table, "Delete status D is not found in the Update record")
            self.assertIn(('C',), update_output_table, "Insert status C is not found in the Update record")
            # verify update asmt_score in fact_table

            update_asmt_score = select([fact_table.c.asmt_score], and_(fact_table.c.student_id == 'f7251065-ca82-4248-9397-cc722e97bbdc', fact_table.c.rec_status == 'C', fact_table.c.asmt_guid == 'a685f0ec-a0a6-4b1e-93b8-0c4298ff6374'))
            new_asmt_score = connection.execute(update_asmt_score).fetchall()
            expected_asmt_score = [(1900,)]
            # verify that score is updated in fact_Asmt
            self.assertEquals(new_asmt_score, expected_asmt_score)
            # verify that there is only one record with status C
            self.assertEquals(len(new_asmt_score), 1)

            # verification for dim_student update : last name change to Bush
            update_last_name = select([dim_student.c.last_name], and_(dim_student.c.student_id == 'f7251065-ca82-4248-9397-cc722e97bbdc', dim_student.c.batch_guid == self.guid_batch_id, dim_student.c.rec_status == "C"))
            result_dim_student = connection.execute(update_last_name).fetchall()
            expected_last_name = [('Bush',)]
            self.assertEquals(result_dim_student, expected_last_name)
            # verify that old recod is deactive
            inactive_rec = select([dim_student], and_(dim_student.c.student_id == 'f7251065-ca82-4248-9397-cc722e97bbdc', dim_student.c.rec_status == "I"))
            inactive_result = connection.execute(inactive_rec).fetchall()
            print(len(inactive_result))

if __name__ == "__main__":
    unittest.main()
