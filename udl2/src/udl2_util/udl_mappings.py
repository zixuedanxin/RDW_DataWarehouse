'''
Created on May 21, 2013

@author: swimberly
'''
from udl2_util.measurement import measure_cpu_plus_elasped_time

@measure_cpu_plus_elasped_time
def get_json_to_asmt_tbl_mappings():
    ''' Return the mappings dict for mapping json file to the assessment integration table '''

    mapping = {'guid_asmt': ['identification', 'guid'],
               'type': ['identification', 'type'],
               'period': ['identification', 'period'],
               'year': ['identification', 'year'],
               'version': ['identification', 'version'],
               'subject': ['identification', 'subject'],
               'name_claim_1': ['claims', 'claim_1', 'name'],
               'name_claim_2': ['claims', 'claim_2', 'name'],
               'name_claim_3': ['claims', 'claim_3', 'name'],
               'name_claim_4': ['claims', 'claim_4', 'name'],
               'name_perf_lvl_1': ['performance_levels', 'level_1', 'name'],
               'name_perf_lvl_2': ['performance_levels', 'level_2', 'name'],
               'name_perf_lvl_3': ['performance_levels', 'level_3', 'name'],
               'name_perf_lvl_4': ['performance_levels', 'level_4', 'name'],
               'name_perf_lvl_5': ['performance_levels', 'level_5', 'name'],
               'score_overall_min': ['overall', 'min_score'],
               'score_overall_max': ['overall', 'max_score'],
               'score_claim_1_min': ['claims', 'claim_1', 'min_score'],
               'score_claim_1_max': ['claims', 'claim_1', 'max_score'],
               'score_claim_1_weight': ['claims', 'claim_1', 'weight'],
               'score_claim_2_min': ['claims', 'claim_2', 'min_score'],
               'score_claim_2_max': ['claims', 'claim_2', 'max_score'],
               'score_claim_2_weight': ['claims', 'claim_2', 'weight'],
               'score_claim_3_min': ['claims', 'claim_3', 'min_score'],
               'score_claim_3_max': ['claims', 'claim_3', 'max_score'],
               'score_claim_3_weight': ['claims', 'claim_3', 'weight'],
               'score_claim_4_min': ['claims', 'claim_4', 'min_score'],
               'score_claim_4_max': ['claims', 'claim_4', 'max_score'],
               'score_claim_4_weight': ['claims', 'claim_4', 'weight'],
               'score_cut_point_1': ['performance_levels', 'level_2', 'cut_point'],
               'score_cut_point_2': ['performance_levels', 'level_3', 'cut_point'],
               'score_cut_point_3': ['performance_levels', 'level_4', 'cut_point'],
               'score_cut_point_4': ['performance_levels', 'level_5', 'cut_point']
           }
    return mapping