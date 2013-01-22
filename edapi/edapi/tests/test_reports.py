'''
Created on Jan 15, 2013

@author: aoren
'''
from edapi.utils import report_config

class TestReport():
    _query = 'test'
        
    @report_config(name="test_report", params=
                                             {
                                                "freeTextField" : {
                                                                   "type" : "string"
                                                                   },
                                                "school_sizes": {"name" : "school_size_report" },
                                                "student_lists": {"name" : "student_list_report" }
                                              }
                                            )
    def generate(self, params):
        return params  # todo: return data
    
    # this report can get retrieved with no configuration, and therefore gets expanded automatically.
    @report_config(name="school_size_report")
    def generate_test_no_config(self, params):
        return ["100", "200", "1000"]
    
    # this report requires configuration, and therefore should NOT get expanded automatically.
    @report_config(name="student_list_report", params={ "scope": {
                                                    "value" : ["State", "Account", "School Group", "School", "Teacher", "Class", "Student", "Grade", "Race", "Custom Attribute"] 
                                                }
                                              })
    def generate_test2(self, params):
        if params['scope'].lower() == "school":
            return { "numberOfStudents" : "200" }
        else:
            return{ "numberOfStudents" : "1000" }
    

