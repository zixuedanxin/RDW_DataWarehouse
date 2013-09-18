'''
Created on Mar 11, 2013

@author: dwu
'''
import unittest
from smarter.reports.compare_pop_report import get_comparing_populations_report,\
    set_default_min_cell_size
from smarter.tests.utils.unittest_with_smarter_sqlite import Unittest_with_smarter_sqlite,\
    UnittestSmarterDBConnection, get_unittest_tenant_name
from smarter.reports.helpers.constants import Constants
from beaker.util import parse_cache_config_options
from beaker.cache import CacheManager
from pyramid.testing import DummyRequest
from pyramid import testing
from edauth.security.session import Session
from smarter.security.roles.teacher import Teacher  # @UnusedImport
from smarter.reports.helpers.compare_pop_stat_report import ComparingPopStatReport


class TestComparingPopulationsStat(Unittest_with_smarter_sqlite):

    def setUp(self):
        cache_opts = {
            'cache.type': 'memory',
            'cache.regions': 'public.data,public.filtered_data,public.shortlived'
        }
        CacheManager(**parse_cache_config_options(cache_opts))

        self.__request = DummyRequest()
        # Must set hook_zca to false to work with unittest_with_sqlite
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        with UnittestSmarterDBConnection() as connection:
            # Insert into user_mapping table
            user_mapping = connection.get_table('user_mapping')
            connection.execute(user_mapping.insert(), user_id='272', guid='272')
        dummy_session = Session()
        dummy_session.set_session_id('123')
        dummy_session.set_roles(['TEACHER'])
        dummy_session.set_uid('272')
        dummy_session.set_tenant(get_unittest_tenant_name())
        self.__config.testing_securitypolicy(dummy_session)
        set_default_min_cell_size(0)

    def tearDown(self):
        # reset the registry
        testing.tearDown()

        # delete user_mapping entries
        with UnittestSmarterDBConnection() as connection:
            user_mapping = connection.get_table('user_mapping')
            connection.execute(user_mapping.delete())

    def test_comparing_populations_with_not_stated_count_district_view(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NY'
        testParam[Constants.DISTRICTGUID] = '229'
        results = ComparingPopStatReport(**testParam).get_report()
        self.assertEqual(results['total'], 35)
        self.assertEqual(results['dmgPrg504'], 2)
        self.assertEqual(results['dmgPrgIep'], 2)
        self.assertEqual(results['dmgPrgLep'], 2)
        self.assertEqual(results['dmgPrgTt1'], 2)
        self.assertEqual(results['ethnicity'], 1)
        self.assertEqual(results['gender'], 0)

    def test_comparing_populations_with_not_stated_count_state_view(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NY'
        results = ComparingPopStatReport(**testParam).get_report()
        self.assertEqual(results['total'], 492)
        self.assertEqual(results['dmgPrg504'], 4)
        self.assertEqual(results['dmgPrgIep'], 5)
        self.assertEqual(results['dmgPrgLep'], 6)
        self.assertEqual(results['dmgPrgTt1'], 5)
        self.assertEqual(results['ethnicity'], 6)
        self.assertEqual(results['gender'], 0)

    def test_comparing_populations_with_not_stated_count_school_view(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NY'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '242'
        results = ComparingPopStatReport(**testParam).get_report()
        self.assertEqual(results['total'], 35)
        self.assertEqual(results['dmgPrg504'], 2)
        self.assertEqual(results['dmgPrgIep'], 3)
        self.assertEqual(results['dmgPrgLep'], 4)
        self.assertEqual(results['dmgPrgTt1'], 3)
        self.assertEqual(results['ethnicity'], 3)
        self.assertEqual(results['gender'], 0)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testReport']
    unittest.main()