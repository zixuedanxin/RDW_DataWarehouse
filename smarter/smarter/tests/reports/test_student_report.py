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
Created on Jan 17, 2013

@author: tosako
'''

import unittest

from pyramid.testing import DummyRequest
from pyramid import testing
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from pyramid.security import Allow
from pyramid.httpexceptions import HTTPForbidden

from smarter.reports.student_report import get_student_report
from edcore.tests.utils.unittest_with_edcore_sqlite import Unittest_with_edcore_sqlite, get_unittest_tenant_name
from edapi.exceptions import NotFoundException
from edauth.tests.test_helper.create_session import create_test_session
import edauth
from smarter_common.security.constants import RolesConstants
from edcore.security.tenant import set_tenant_map
from smarter.security.roles.default import DefaultRole  # @UnusedImport
from smarter.security.roles.pii import PII  # @UnusedImport


class TestStudentReport(Unittest_with_edcore_sqlite):

    def setUp(self):
        cache_opts = {
            'cache.type': 'memory',
            'cache.regions': 'public.data,public.filtered_data,public.shortlived'
        }

        CacheManager(**parse_cache_config_options(cache_opts))

        self.__request = DummyRequest()
        # Must set hook_zca to false to work with uniittest_with_sqlite
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        defined_roles = [(Allow, RolesConstants.PII, ('view', 'logout'))]
        edauth.set_roles(defined_roles)
        set_tenant_map({get_unittest_tenant_name(): 'NC'})
        # Set up context security
        dummy_session = create_test_session([RolesConstants.PII])
        self.__config.testing_securitypolicy(dummy_session.get_user())

    def tearDown(self):
        # reset the registry
        testing.tearDown()

    def test_invalid_params(self):
        params = {"studentId": 'dae1acf4-afb0-4013-90ba-9dcde4b25621', "assessmentGuid": '3b10d26b-b013-4cdd-a916-5d577e895ed4', 'stateCode': 'AA'}
        results = get_student_report(params)
        self.assertIsInstance(results, HTTPForbidden)

    def test_student_report(self):
        params = {"studentId": 'dae1acf4-afb0-4013-90ba-9dcde4b25621', "assessmentGuid": '3b10d26b-b013-4cdd-a916-5d577e895ed4', 'stateCode': 'NC'}
        result = get_student_report(params)['all_results']
        self.assertEqual(1, len(result), "studentId should have 1 report")
        self.assertEqual('ELA', result[0]['asmt_subject'], 'asmt_subject')
        self.assertEqual('2200', result[0]['claims'][0]['score'], 'asmt_claim_1_score 88')
        self.assertEqual('Research & Inquiry', result[0]['claims'][3]['name'], 'asmt_claim_4_name Spelling')

    def test_student_report_iab(self):
        params = {"studentId": '34b99412-fd5b-48f0-8ce8-f8ca3788634a', 'asmtType': 'INTERIM ASSESSMENT BLOCKS', 'stateCode': 'NC'}
        result = get_student_report(params)['all_results']
        self.assertEqual('Interim Assessment Blocks', result['asmt_type'], 'asmt_type')
        self.assertEqual('34b99412-fd5b-48f0-8ce8-f8ca3788634a', result['student_id'], 'student_id')
        self.assertEqual(10, len(result), "IAB result for this studentId should have 8 objects")

    def test_assessment_header_info(self):
        params = {"studentId": 'dae1acf4-afb0-4013-90ba-9dcde4b25621', 'stateCode': 'NC'}
        result = get_student_report(params)
        student_report = result['all_results'][0]

        self.assertEqual('Math', student_report['asmt_subject'], 'asmt_subject')

    def test_custom_metadata(self):
        params = {"studentId": 'dae1acf4-afb0-4013-90ba-9dcde4b25621', "stateCode": 'NC'}
        result = get_student_report(params)['all_results']
        student_report = result[0]

        cut_points_list = student_report['cut_point_intervals']
        self.assertEqual(4, len(cut_points_list), "we should have 4 cut point intervals")

        expected_cut_point_names = set(['Minimal Understanding', 'Partial Understanding', 'Adequate Understanding', 'Thorough Understanding'])
        for cut_point in cut_points_list:
            self.assertIsInstance(cut_point, dict, "each cut point should be a dictionary")

            keys = cut_point.keys()
            cut_point_name = cut_point['name']
            self.assertIn(cut_point_name.strip(), expected_cut_point_names, "unexpected cut point name")
            self.assertIn("name", keys, "should contain the name of the cut point")
            self.assertIn("interval", keys, "should contain the value of the cut point")
            self.assertIn("text_color", keys, "should contain the text_color of the cut point")
            self.assertIn("end_gradient_bg_color", keys, "should contain the end_gradient_bg_color of the cut point")
            self.assertIn("start_gradient_bg_color", keys, "should contain the start_gradient_bg_color of the cut point")
            self.assertIn("bg_color", keys, "should contain the bg_color of the cut point")

    def test_score_interval(self):
        params = {"studentId": 'dae1acf4-afb0-4013-90ba-9dcde4b25621', 'stateCode': 'NC'}
        result = get_student_report(params)['all_results']
        student_report = result[0]

        self.assertEqual(student_report['asmt_score'], student_report['asmt_score_range_min'] + student_report['asmt_score_interval'])
        self.assertEqual(student_report['asmt_score'], student_report['asmt_score_range_max'] - student_report['asmt_score_interval'])

    def test_context(self):
        params = {"studentId": 'dae1acf4-afb0-4013-90ba-9dcde4b25621', 'stateCode': 'NC'}
        result = get_student_report(params)['context']['items']
        self.assertEqual('North Carolina', result[1]['name'])
        self.assertEqual('Sunset School District', result[2]['name'])
        self.assertEqual("03", result[4]['name'])
        self.assertEqual("Sunset - Eastern Elementary", result[3]['name'])
        self.assertEqual("Lettie L. Hose", result[5]['name'])

    def test_claims(self):
        params = {"studentId": 'eac5d0d6-0bba-43cd-81cd-8b1956b9177e', 'stateCode': 'NC'}
        items = get_student_report(params)['all_results']
        result = items[0]
        self.assertEqual(3, len(result['claims']))
        self.assertEqual('Concepts & Procedures', result['claims'][0]['name'])
        self.assertEqual('Problem Solving and Modeling & Data Analysis', result['claims'][1]['name'])
        self.assertEqual('Communicating Reasoning', result['claims'][2]['name'])
        result = items[1]
        self.assertEqual(4, len(result['claims']))
        self.assertEqual('Reading', result['claims'][0]['name'])
        self.assertEqual('Writing', result['claims'][1]['name'])
        self.assertEqual('Listening', result['claims'][2]['name'])
        self.assertEqual('Research & Inquiry', result['claims'][3]['name'])
        self.assertEqual(6, len(result['accommodations']))
        self.assertEqual(4, len(result['accommodations'][0]))
        self.assertEqual(1, len(result['accommodations'][9]))
        self.assertEqual(2, len(result['accommodations'][15]))
        self.assertEqual(5, len(result['accommodations'][16]))
        self.assertEqual(1, len(result['accommodations'][25]))
        self.assertEqual(2, len(result['accommodations'][26]))

    def test_invalid_student_id(self):
        params = {'studentId': 'invalid', 'stateCode': 'NC'}
        self.assertRaises(NotFoundException, get_student_report, params)

if __name__ == '__main__':
    unittest.main()
