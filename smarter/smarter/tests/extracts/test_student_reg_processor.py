from pyramid.security import Allow
import edauth
from edauth.security.user import User
from edcore.security.tenant import set_tenant_map
from edextract.tasks.student_reg_constants import Constants as TaskConstants, ReportType
from smarter.extracts.student_reg_processor import _create_task_info, process_async_extraction_request, _get_extract_file_path

__author__ = 'ablum'

from pyramid.testing import DummyRequest
from pyramid import testing
from edcore.tests.utils.unittest_with_edcore_sqlite import \
    Unittest_with_edcore_sqlite
from pyramid.registry import Registry
from edcore.tests.utils.unittest_with_stats_sqlite import Unittest_with_stats_sqlite
import tempfile
from edextract.celery import setup_celery
from beaker.cache import CacheManager, cache_managers
from beaker.util import parse_cache_config_options
from edauth.tests.test_helper.create_session import create_test_session


class TestStudentRegProcessor(Unittest_with_edcore_sqlite, Unittest_with_stats_sqlite):

    def setUp(self):
        self.reg = Registry()
        self.__work_zone_dir = tempfile.TemporaryDirectory()
        self.reg.settings = {'extract.work_zone_base_dir': '/tmp/work_zone',
                             'pickup.gatekeeper.t1': '/t/acb',
                             'pickup.gatekeeper.t2': '/a/df',
                             'pickup.gatekeeper.y': '/a/c',
                             'pickup.sftp.hostname': 'hostname.local.net',
                             'pickup.sftp.user': 'myUser',
                             'pickup.sftp.private_key_file': '/home/users/myUser/.ssh/id_rsa',
                             'extract.available_grades': '3,4,5,6,7,8,11'}
        settings = {'extract.celery.CELERY_ALWAYS_EAGER': True}
        setup_celery(settings)
        cache_opts = {
            'cache.type': 'memory',
            'cache.regions': 'public.data,public.filtered_data,public.shortlived'
        }
        CacheManager(**parse_cache_config_options(cache_opts))
        # Set up user context
        self.__request = DummyRequest()
        # Must set hook_zca to false to work with unittest_with_sqlite
        self.__config = testing.setUp(registry=self.reg, request=self.__request, hook_zca=False)
        dummy_session = create_test_session(['STATE_EDUCATION_ADMINISTRATOR_1'])
        defined_roles = [(Allow, 'STATE_EDUCATION_ADMINISTRATOR_1', ('view', 'logout'))]
        edauth.set_roles(defined_roles)
        self.__config.testing_securitypolicy(dummy_session.get_user())
        set_tenant_map({'tomcat': 'NC'})

    def tearDown(self):
        # reset the registry
        testing.tearDown()
        cache_managers.clear()

    @classmethod
    def setUpClass(cls):
        Unittest_with_edcore_sqlite.setUpClass()
        Unittest_with_stats_sqlite.setUpClass()

    def test__create_task_info(self):
        params = {'stateCode': 'NC',
                  'academicYear': [2015]}
        user = User()
        results = _create_task_info("request_id", user, 'tenant', params)
        self.assertEqual(len(results), 4)

    def test__get_extract_file_path(self):
        extract_params = {TaskConstants.STATE_CODE: "NC",
                          TaskConstants.ACADEMIC_YEAR: 2015,
                          TaskConstants.REPORT_TYPE: ReportType.STATISTICS}

        result = _get_extract_file_path("requestId", "tenant", extract_params)
        self.assertIn('.csv', result)
        self.assertIn('requestId', result)
        self.assertIn('tenant', result)
        self.assertIn('NC', result)

    def test_process_async_extraction_request(self):
        params = {'stateCode': ['NC'],
                  'academicYear': [2015]}
        response = process_async_extraction_request(params)
        self.assertIn('.zip.gpg', response['fileName'])
        self.assertEqual(response['tasks'][0]['status'], 'ok')
        self.assertEqual(response['tasks'][0]['academicYear'], 2015)