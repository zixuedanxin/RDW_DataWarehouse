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
Created on Mar 14, 2013

@author: dip
'''
import unittest
from pyramid import testing
from pyramid.testing import DummyRequest
from edapi.decorators import user_info, validate_params
from edapi.tests.dummy import DummyUser
from edapi.httpexceptions import EdApiHTTPPreconditionFailed


@user_info
def some_func():
    return {}


@user_info
def some_func_with_some_results():
    return {'some': 'thing'}


class TestDecorators(unittest.TestCase):

    def setUp(self):
        self.__request = DummyRequest()
        self.__config = testing.setUp(request=self.__request, hook_zca=False)

    def tearDown(self):
        # reset the registry
        testing.tearDown()

    def test_user_info(self):
        dummy_user = DummyUser()
        self.__config.testing_securitypolicy(dummy_user, ['TEACHER'])
        results = some_func()
        self.assertIsInstance(results['user_info'], DummyUser)

    def test_user_info_with_no_user(self):
        self.__config.testing_securitypolicy(None, ['TEACHER'])
        results = some_func()
        self.assertEqual(results, {})

    def test_user_with_some_results(self):
        dummy_user = DummyUser()
        self.__config.testing_securitypolicy(dummy_user, ['TEACHER'])
        results = some_func_with_some_results()
        self.assertEquals(len(results), 2)
        self.assertDictContainsSubset(some_func_with_some_results(), results)
        self.assertIsInstance(results['user_info'], DummyUser)

    def test_validate_params(self):
        # test params
        params = {'param0': 'value0', 'param2': "2"}
        # test with value
        dummy_request = DummyRequest(params)

        def dummy_handler(*args, **kwargs):
            return args[0]

        request_handler = validate_params({
            'type': 'object',
            'properties': {
                'param0': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    }
                },
                'param2': {
                    'type': 'integer',
                }
            },
            'required': ['param0']
        })(dummy_handler)
        req = request_handler(dummy_request)
        self.assertEqual(req, dummy_request)
        self.assertEqual(req.validated_params, {'param0': ['value0'], 'param2': 2})
        # test without value
        try:
            dummy_request = DummyRequest({'param0': 'value0'})
            request_handler = validate_params({
                'type': 'object',
                'properties': {
                    'param1': {
                        'type': 'array',
                        'items': {
                            'type': 'string'
                        }
                    }
                },
                'required': ['param1']
            })(dummy_handler)
        except EdApiHTTPPreconditionFailed as e:
            self.assertEqual(True, True)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
