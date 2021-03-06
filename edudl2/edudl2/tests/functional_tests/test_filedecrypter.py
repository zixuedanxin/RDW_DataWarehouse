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

import os
import shutil
import tempfile
from edudl2.filedecrypter import file_decrypter
from edudl2.tests.functional_tests import UDLFunctionalTestCase


class TestFileDecrypter(UDLFunctionalTestCase):

    def setUp(self):
        # temp directory for testing decrypter
        self.decrypter_test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.decrypter_test_dir, ignore_errors=True)

    def test_decrypter_for_valid_file(self):
        gpg_file = self.require_gpg_file('test_source_file_tar_gzipped')
        self.assertTrue(os.path.isfile(gpg_file))
        status, decrypted_file = file_decrypter.decrypt_file(gpg_file, self.decrypter_test_dir, 'sbac udl2', self.gpg_home)
        self.assertTrue(os.path.isfile(decrypted_file))
        self.assertTrue(status.ok)
        self.assertEqual(status.trust_level, 4)
        self.assertEqual(status.trust_text, 'TRUST_ULTIMATE')
        self.assertEqual(status.username, 'Autogenerated Key <ca_user@ca.com>')
        self.assertEqual(status.fingerprint, '398AE2A8E54D810502E4B115DD87CFFF75C7BEC2')

    def test_decrypter_for_invalid_file(self):
        test_invalid_data = os.path.join(self.data_dir, 'test_non_existing_file_tar_gzipped.tar.gz.gpg')
        self.assertFalse(os.path.isfile(test_invalid_data))
        self.assertRaises(Exception, file_decrypter.decrypt_file, test_invalid_data, self.decrypter_test_dir, 'sbac udl2', self.gpg_home)

    def test_decrypter_for_corrupted_file(self):
        test_corrupted_file = os.path.join(self.data_dir, 'test_corrupted_source_file_tar_gzipped.tar.gz.gpg')
        self.assertTrue(os.path.isfile(test_corrupted_file))
        self.assertRaises(Exception, file_decrypter.decrypt_file, test_corrupted_file, self.decrypter_test_dir, 'sbac udl2', self.gpg_home)

    def test_decrypter_with_wrong_passphrase(self):
        gpg_file = self.require_gpg_file('test_source_file_tar_gzipped')
        self.assertTrue(os.path.isfile(gpg_file))
        self.assertRaises(Exception, file_decrypter.decrypt_file, gpg_file, self.decrypter_test_dir, 'wrong passphrase', self.gpg_home)
