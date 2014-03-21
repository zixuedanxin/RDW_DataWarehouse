"""
SBAC-specific hierarchy configuration.

@author: nestep
@date: March 4, 2014
"""


STATE_TYPES = {'california': {'district_types_and_counts': {'Big Average': 50, 'Big Poor': 25, 'Big Good': 50,
                                                            'Medium Average': 50, 'Medium Poor': 25, 'Medium Good': 25,
                                                            'Medium Very Poor': 50, 'Medium Very Good': 50,
                                                            'Small Average': 25, 'Small Poor': 50, 'Small Good': 25,
                                                            'Small Very Poor': 50, 'Small Very Good': 50},
                             'subject_skip_percentages': {'Math': .04, 'ELA': .03},
                             'demographics': 'california'},
               'devel': {'district_types_and_counts': {'Small Average': 4},
                         'subject_skip_percentages': {'Math': .04, 'ELA': .03},
                         'demographics': 'california'}
               }