# (c) 2014 The Regents of the University of California. All rights reserved,
# subject to the license below.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0. Unless required by
# applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

'''
Created on Nov 8, 2013

@author: dip
'''
import unittest

from pyramid.testing import DummyRequest
from pyramid import testing
from pyramid.registry import Registry
from sqlalchemy.sql.expression import select
from pyramid.security import Allow

from smarter.extracts.student_assessment import get_extract_assessment_query, \
    get_extract_assessment_item_and_raw_query, get_extract_assessment_query_iab
from edcore.utils.utils import compile_query_to_sql_text
from edcore.tests.utils.unittest_with_edcore_sqlite import Unittest_with_edcore_sqlite,\
    UnittestEdcoreDBConnection, get_unittest_tenant_name
from edauth.tests.test_helper.create_session import create_test_session
from edauth.security.user import RoleRelation
import edauth
from smarter_common.security.constants import RolesConstants
from edcore.security.tenant import set_tenant_map
from smarter.security.roles.pii import PII  # @UnusedImport
from smarter.security.roles.state_level import StateLevel  # @UnusedImport
from smarter.extracts.constants import ExtractType


class TestStudentAssessment(Unittest_with_edcore_sqlite):

    def setUp(self):
        self.__request = DummyRequest()
        # Must set hook_zca to false to work with uniittest_with_sqlite
        reg = Registry()
        reg.settings = {}
        self.__config = testing.setUp(registry=reg, request=self.__request, hook_zca=False)
        self.__tenant_name = get_unittest_tenant_name()
        defined_roles = [(Allow, RolesConstants.SAR_EXTRACTS, ('view', 'logout')),
                         (Allow, RolesConstants.ITEM_LEVEL_EXTRACTS, ('view', 'logout')),
                         (Allow, RolesConstants.ITEM_LEVEL_EXTRACTS, ('view', 'logout'))]
        edauth.set_roles(defined_roles)
        set_tenant_map({get_unittest_tenant_name(): 'NC'})
        # Set up context security
        dummy_session = create_test_session([RolesConstants.SAR_EXTRACTS])
        dummy_session.set_user_context([RoleRelation(RolesConstants.SAR_EXTRACTS, get_unittest_tenant_name(), "NC", None, None),
                                        RoleRelation(RolesConstants.AUDIT_XML_EXTRACTS, get_unittest_tenant_name(), "NC", None, None),
                                        RoleRelation(RolesConstants.ITEM_LEVEL_EXTRACTS, get_unittest_tenant_name(), "NC", None, None)])
        self.__config.testing_securitypolicy(dummy_session.get_user())

    def tearDown(self):
        self.__request = None
        testing.tearDown()

    def test_get_extract_assessment_query_iab(self):
        params = {'stateCode': 'NC',
                  'asmtYear': '2019',
                  'asmtType': 'INTERIM ASSESSMENT BLOCKS',
                  'asmtSubject': 'Math',
                  'extractType': 'studentAssessment'}
        query = get_extract_assessment_query_iab(params)
        self.assertIsNotNone(query)
        self.assertIn('fact_block_asmt_outcome.asmt_type', str(query._whereclause))

    def test_get_extract_assessment_query_results_iab(self):
        params = {'stateCode': 'NC',
                  'asmtYear': '2015',
                  'asmtType': 'INTERIM ASSESSMENT BLOCKS',
                  'asmtSubject': 'Math',
                  'asmt_grade': '03'}
        query = get_extract_assessment_query_iab(params)
        self.assertIsNotNone(query)
        with UnittestEdcoreDBConnection() as connection:
            results = connection.get_result(query)
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)
        self.assertEqual('ab06bc40-5372-11e4-916c-0800200c9a66', results[0]['AssessmentGuid'])
        self.assertEqual('INTERIM ASSESSMENT BLOCKS', results[0]['AssessmentType'])

    def test_get_extract_assessment_query(self):
        params = {'stateCode': 'NC',
                  'asmtYear': '2019',
                  'asmtType': 'SUMMATIVE',
                  'asmtSubject': 'Math',
                  'extractType': 'studentAssessment'}
        query = get_extract_assessment_query(params)
        self.assertIsNotNone(query)
        self.assertIn('fact_asmt_outcome_vw.asmt_type', str(query._whereclause))

    def test_get_extract_assessment_query_limit(self):
        params = {'stateCode': 'NC',
                  'asmtYear': '2015',
                  'asmtType': 'SUMMATIVE',
                  'asmtSubject': 'Math',
                  'extractType': 'studentAssessment'}
        query = get_extract_assessment_query(params).limit(541)
        self.assertIsNotNone(query)
        self.assertIn('541', str(query._limit))

    def test_get_extract_assessment_query_compiled(self):
        params = {'stateCode': 'NC',
                  'asmtYear': '2015',
                  'asmtType': 'SUMMATIVE',
                  'asmtSubject': 'Math',
                  'extractType': 'studentAssessment'}
        query = compile_query_to_sql_text(get_extract_assessment_query(params))
        self.assertIsNotNone(query)
        self.assertIsInstance(query, str)
        self.assertIn('SUMMATIVE', query)

    def test_compile_query_to_sql_text(self):
        with UnittestEdcoreDBConnection() as connection:
            fact = connection.get_table('fact_asmt_outcome_vw')
            query = select([fact.c.state_code], from_obj=[fact])
            query = query.where(fact.c.state_code == 'UT')
            str_query = compile_query_to_sql_text(query)
            self.assertIn("fact_asmt_outcome_vw.state_code = 'UT'", str_query)

    def test_get_extract_assessment_query_results(self):
        params = {'stateCode': 'NC',
                  'asmtYear': '2015',
                  'asmtType': 'SUMMATIVE',
                  'asmtSubject': 'Math',
                  'asmt_grade': '03'}
        query = get_extract_assessment_query(params)
        self.assertIsNotNone(query)
        with UnittestEdcoreDBConnection() as connection:
            results = connection.get_result(query)
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)
        # Check for columns are in results
        self.assertIn('AccommodationStreamlineMode', results[0])
        self.assertIn('AccommodationClosedCaptioning', results[0])

    def test_get_extract_assessment_query_with_filters(self):
        params = {'stateCode': 'NC',
                  'asmtYear': '2016',
                  'asmtType': 'SUMMATIVE',
                  'asmtSubject': 'Math',
                  'sex': ['male']}
        query = get_extract_assessment_query(params)
        self.assertIsNotNone(query)
        with UnittestEdcoreDBConnection() as connection:
            results = connection.get_result(query)
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)

    def test_get_extract_assessment_query_with_selections(self):
        params = {'stateCode': 'NC',
                  'districtId': '229',
                  'schoolId': '939',
                  'asmtGrade': '07',
                  'asmtYear': '2016',
                  'asmtType': 'SUMMATIVE',
                  'asmtSubject': 'Math',
                  'studentId': ['a629ca88-afe6-468c-9dbb-92322a284602'],
                  'group1Id': ['d20236e0-eb48-11e3-ac10-0800200c9a66']}
        query = get_extract_assessment_query(params)
        self.assertIsNotNone(query)
        with UnittestEdcoreDBConnection() as connection:
            results = connection.get_result(query)
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)

    def test_get_extract_items_query(self):
        params = {'stateCode': 'NC',
                  'asmtYear': '2019',
                  'asmtType': 'SUMMATIVE',
                  'asmtSubject': 'Math',
                  'asmtGrade': '03',
                  'extractType': 'itemLevel'}
        query = get_extract_assessment_item_and_raw_query(params, ExtractType.itemLevel)
        self.assertIsNotNone(query)
        self.assertIn('fact_asmt_outcome_vw.asmt_type', str(query._whereclause))

    def test_get_extract_items_query_limit(self):
        params = {'stateCode': 'NC',
                  'asmtYear': '2015',
                  'asmtType': 'SUMMATIVE',
                  'asmtSubject': 'Math',
                  'asmtGrade': '03',
                  'extractType': 'itemLevel'}
        query = get_extract_assessment_item_and_raw_query(params, ExtractType.itemLevel).limit(541)
        self.assertIsNotNone(query)
        self.assertIn('541', str(query._limit))

    def test_get_extract_items_query_compiled(self):
        params = {'stateCode': 'NC',
                  'asmtYear': '2015',
                  'asmtType': 'SUMMATIVE',
                  'asmtSubject': 'Math',
                  'asmtGrade': '03',
                  'extractType': 'itemLevel'}
        query = compile_query_to_sql_text(get_extract_assessment_item_and_raw_query(params, ExtractType.itemLevel))
        self.assertIsNotNone(query)
        self.assertIsInstance(query, str)
        self.assertIn('SUMMATIVE', query)

    def test_get_extract_items_query_results(self):
        params = {'stateCode': 'NC',
                  'asmtYear': '2015',
                  'asmtType': 'SUMMATIVE',
                  'asmtSubject': 'Math',
                  'asmtGrade': '03'}
        query = get_extract_assessment_item_and_raw_query(params, ExtractType.itemLevel)
        self.assertIsNotNone(query)
        with UnittestEdcoreDBConnection() as connection:
            results = connection.get_result(query)
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)
        # Check for columns are in results
        self.assertIn('district_id', results[0])
        self.assertIn('student_id', results[0])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
