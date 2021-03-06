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

"""
This module describes the unit tests for the csv_writer module.
"""

import unittest
import tempfile
import shutil
import os
import csv
from edcore.utils.csv_writer import write_csv


class TestCSVWriter(unittest.TestCase):

    def setUp(self):
        self.__tmp_dir = tempfile.mkdtemp('csv_filewriter_test')

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir)

    def test_write_csv(self):
        output = os.path.join(self.__tmp_dir, 'asmt_extract.csv')
        header = ['asmt_guid', 'asmt_grade', 'state_name', 'state_code', 'district_id', 'district_name', 'school_id', 'school_name']
        data = [
            ['1-2-3', 'F', 'New Jersey', 'NJ', 'a-b-c', 'Jersey City', 'i-ii-iii', 'Newport School'],
            ['1-2-3', 'A', 'New Jersey', 'NJ', 'd-e-f', 'Hoboken', 'iv-v-vi', 'Sinatra School'],
            ['1-2-3', 'B', 'New Jersey', 'NJ', 'g-h-i', 'Bayonne', 'vii-viii-ix', 'Bayonne School']
        ]
        with open(output, 'w') as f:
            write_csv(f, data, header=header)

        self.assertTrue(os.path.exists(output))
        csv_data = []
        with open(output) as out:
            csv_rows = csv.reader(out)
            for row in csv_rows:
                csv_data.append(row)
        self.assertEqual(len(csv_data), 4)
        self.assertEqual(header, csv_data[0])
        self.assertEqual(data[0], csv_data[1])
        self.assertEqual(data[1], csv_data[2])
        self.assertEqual(data[2], csv_data[3])
