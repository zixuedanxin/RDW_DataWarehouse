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

"""
Track the counts for grade category
"""

from edextract.student_reg_extract_processors.attribute_constants import AttributeFieldConstants, AttributeValueConstants
from edextract.student_reg_extract_processors.category_constants import CategoryNameConstants, CategoryValueConstants
from edextract.trackers.category_tracker import CategoryTracker


class GradeKTracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.GRADEK, CategoryValueConstants.TOTAL, AttributeFieldConstants.GRADE)

    def _should_increment(self, row):
        return row[AttributeFieldConstants.GRADE].upper() == AttributeValueConstants.GRADEK


class Grade1Tracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.GRADE1, CategoryValueConstants.TOTAL, AttributeFieldConstants.GRADE)

    def _should_increment(self, row):
        return row[AttributeFieldConstants.GRADE] == AttributeValueConstants.GRADE1


class Grade2Tracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.GRADE2, CategoryValueConstants.TOTAL, AttributeFieldConstants.GRADE)

    def _should_increment(self, row):
        return row[AttributeFieldConstants.GRADE] == AttributeValueConstants.GRADE2


class Grade3Tracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.GRADE3, CategoryValueConstants.TOTAL, AttributeFieldConstants.GRADE)

    def _should_increment(self, row):
        return row[AttributeFieldConstants.GRADE] == AttributeValueConstants.GRADE3


class Grade4Tracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.GRADE4, CategoryValueConstants.TOTAL, AttributeFieldConstants.GRADE)

    def _should_increment(self, row):
        return row[AttributeFieldConstants.GRADE] == AttributeValueConstants.GRADE4


class Grade5Tracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.GRADE5, CategoryValueConstants.TOTAL, AttributeFieldConstants.GRADE)

    def _should_increment(self, row):
        return row[AttributeFieldConstants.GRADE] == AttributeValueConstants.GRADE5


class Grade6Tracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.GRADE6, CategoryValueConstants.TOTAL, AttributeFieldConstants.GRADE)

    def _should_increment(self, row):
        return row[AttributeFieldConstants.GRADE] == AttributeValueConstants.GRADE6


class Grade7Tracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.GRADE7, CategoryValueConstants.TOTAL, AttributeFieldConstants.GRADE)

    def _should_increment(self, row):
        return row[AttributeFieldConstants.GRADE] == AttributeValueConstants.GRADE7


class Grade8Tracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.GRADE8, CategoryValueConstants.TOTAL, AttributeFieldConstants.GRADE)

    def _should_increment(self, row):
        return row[AttributeFieldConstants.GRADE] == AttributeValueConstants.GRADE8


class Grade9Tracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.GRADE9, CategoryValueConstants.TOTAL, AttributeFieldConstants.GRADE)

    def _should_increment(self, row):
        return row[AttributeFieldConstants.GRADE] == AttributeValueConstants.GRADE9


class Grade10Tracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.GRADE10, CategoryValueConstants.TOTAL, AttributeFieldConstants.GRADE)

    def _should_increment(self, row):
        return row[AttributeFieldConstants.GRADE] == AttributeValueConstants.GRADE10


class Grade11Tracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.GRADE11, CategoryValueConstants.TOTAL, AttributeFieldConstants.GRADE)

    def _should_increment(self, row):
        return row[AttributeFieldConstants.GRADE] == AttributeValueConstants.GRADE11


class Grade12Tracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.GRADE12, CategoryValueConstants.TOTAL, AttributeFieldConstants.GRADE)

    def _should_increment(self, row):
        return row[AttributeFieldConstants.GRADE] == AttributeValueConstants.GRADE12
