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

__author__ = 'npandey'

import unittest
from edextract.trackers.grade_tracker import (GradeKTracker, Grade1Tracker, Grade2Tracker, Grade3Tracker, Grade4Tracker,
                                              Grade5Tracker, Grade6Tracker, Grade7Tracker, Grade8Tracker, Grade9Tracker,
                                              Grade10Tracker, Grade11Tracker, Grade12Tracker)


class TestGradeTrackers(unittest.TestCase):
    def setUp(self):
        self.gradek = GradeKTracker()
        self.grade1 = Grade1Tracker()
        self.grade2 = Grade2Tracker()
        self.grade3 = Grade3Tracker()
        self.grade4 = Grade4Tracker()
        self.grade5 = Grade5Tracker()
        self.grade6 = Grade6Tracker()
        self.grade7 = Grade7Tracker()
        self.grade8 = Grade8Tracker()
        self.grade9 = Grade9Tracker()
        self.grade10 = Grade10Tracker()
        self.grade11 = Grade11Tracker()
        self.grade12 = Grade12Tracker()

        self.grade_trackers = [self.gradek, self.grade1, self.grade2, self.grade3, self.grade4, self.grade5, self.grade6,
                               self.grade7, self.grade8, self.grade9, self.grade10, self.grade11, self.grade12]

        self.grade_db_rows = [{'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'enrl_grade': 'KG'},
                              {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'enrl_grade': '01'},
                              {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'enrl_grade': '03'},
                              {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'enrl_grade': '04'},
                              {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'enrl_grade': '05'},
                              {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'enrl_grade': '06'},
                              {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'enrl_grade': '07'},
                              {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'enrl_grade': '08'},
                              {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'enrl_grade': '09'},
                              {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'enrl_grade': '10'},
                              {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'enrl_grade': '11'},
                              {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2014, 'enrl_grade': '03'},
                              {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2014, 'enrl_grade': '07'},
                              {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2014, 'enrl_grade': '09'},
                              {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2014, 'enrl_grade': '12'}]

    def test_grade_trackers(self):
        for tracker in self.grade_trackers:
            for row in self.grade_db_rows:
                tracker.track_academic_year('NJ', row)

        self.assertEqual(1, len(self.gradek.get_map_entry('NJ')))
        self.assertEqual(1, len(self.grade1.get_map_entry('NJ')))
        self.assertIsNone(self.grade2.get_map_entry('NJ'))
        self.assertEqual(2, len(self.grade3.get_map_entry('NJ')))
        self.assertEqual(1, len(self.grade4.get_map_entry('NJ')))
        self.assertEqual(1, len(self.grade5.get_map_entry('NJ')))
        self.assertEqual(1, len(self.grade6.get_map_entry('NJ')))
        self.assertEqual(2, len(self.grade7.get_map_entry('NJ')))
        self.assertEqual(1, len(self.grade8.get_map_entry('NJ')))
        self.assertEqual(2, len(self.grade9.get_map_entry('NJ')))
        self.assertEqual(1, len(self.grade10.get_map_entry('NJ')))
        self.assertEqual(1, len(self.grade11.get_map_entry('NJ')))
        self.assertEqual(1, len(self.grade12.get_map_entry('NJ')))

        self.assertEqual(1, self.grade1.get_map_entry('NJ')[2013])
        self.assertEqual(1, self.grade3.get_map_entry('NJ')[2013])
        self.assertEqual(1, self.grade12.get_map_entry('NJ')[2014])
        self.assertEqual(1, self.grade3.get_map_entry('NJ')[2014])
        self.assertEqual(1, self.grade7.get_map_entry('NJ')[2014])
        self.assertEqual(1, self.grade9.get_map_entry('NJ')[2014])
        self.assertEqual(1, self.grade5.get_map_entry('NJ')[2013])

    def test_grade_case(self):
        row1 = {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'enrl_grade': 'kg'}
        row2 = {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'enrl_grade': 'Kg'}
        row3 = {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'enrl_grade': 'kG'}
        self.gradek.track_academic_year('school1', row1)
        self.gradek.track_academic_year('school1', row2)
        self.gradek.track_academic_year('school1', row3)

        self.assertEqual(1, len(self.gradek.get_map_entry('school1')))
        self.assertEqual(3, self.gradek.get_map_entry('school1')[2013])
