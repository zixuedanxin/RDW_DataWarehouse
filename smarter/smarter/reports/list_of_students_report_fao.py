# (c) 2014 The Regents of the University of California. All rights reserved,
# subject to the license below.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0. Unless required by
# applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

'''
Created on Oct 21, 2014

@author: tosako
'''
from smarter.reports.helpers.constants import Constants, AssessmentType
from edcore.database.edcore_connector import EdCoreDBConnection
from smarter.security.context import select_with_context
from sqlalchemy.sql.expression import and_, desc, or_, null
from smarter.reports.helpers.filters import apply_filter_to_query, \
    get_student_demographic
from smarter.reports.helpers.assessments import get_claims, get_cut_points, \
    get_overall_asmt_interval
from edapi.cache import cache_region
from smarter.reports.helpers.metadata import get_subjects_map, \
    get_custom_metadata
from smarter.reports.list_of_students_report_utils import get_group_filters, \
    __reverse_map
from smarter.reports.helpers.breadcrumbs import get_breadcrumbs_context
from smarter.reports.student_administration import get_asmt_administration_years, \
    get_asmt_academic_years
from smarter.reports.helpers.compare_pop_stat_report import get_not_stated_count
from smarter_common.security.constants import RolesConstants
from string import capwords
from sqlalchemy.sql.functions import func


def get_list_of_students_report_fao(params):
    stateCode = str(params[Constants.STATECODE])
    districtId = str(params[Constants.DISTRICTGUID])
    schoolId = str(params[Constants.SCHOOLGUID])
    asmtGrade = params.get(Constants.ASMTGRADE)
    asmtSubject = params.get(Constants.ASMTSUBJECT)
    asmtYear = params.get(Constants.ASMTYEAR)
    results = get_list_of_students_fao(params)
    subjects_map = get_subjects_map(asmtSubject)
    asmt_data = __get_asmt_data(results)
    los_results = {}
    los_results['assessments'] = format_assessments_fao(results, subjects_map)
    los_results['groups'] = get_group_filters(results)

    # color metadata
    custom_metadata_map = get_custom_metadata(stateCode, None)
    los_results[Constants.METADATA] = __format_cut_points(asmt_data, subjects_map, custom_metadata_map)
    los_results[Constants.CONTEXT] = get_breadcrumbs_context(state_code=stateCode, district_id=districtId, school_id=schoolId, asmt_grade=asmtGrade)
    los_results[Constants.SUBJECTS] = __reverse_map(subjects_map)

    # Additional queries for LOS report
    los_results[Constants.ASMT_ADMINISTRATION] = get_asmt_administration_years(stateCode, districtId, schoolId, asmtGrade, asmt_year=asmtYear)
    los_results[Constants.NOT_STATED] = get_not_stated_count(params)
    los_results[Constants.ASMT_PERIOD_YEAR] = get_asmt_academic_years(stateCode)
    return los_results


def get_list_of_students_fao(params):
    stateCode = str(params[Constants.STATECODE])
    districtId = str(params[Constants.DISTRICTGUID])
    schoolId = str(params[Constants.SCHOOLGUID])
    asmtGrade = params.get(Constants.ASMTGRADE)
    asmtSubject = params.get(Constants.ASMTSUBJECT)
    asmtYear = params.get(Constants.ASMTYEAR)

    with EdCoreDBConnection(state_code=stateCode) as connector:
        # get handle to tables
        dim_student = connector.get_table(Constants.DIM_STUDENT)
        dim_asmt = connector.get_table(Constants.DIM_ASMT)
        fact_asmt_outcome_vw = connector.get_table(Constants.FACT_ASMT_OUTCOME_VW)
        query = select_with_context([
            dim_student.c.student_id.label('student_id'),
            dim_student.c.first_name.label('first_name'),
            dim_student.c.middle_name.label('middle_name'),
            dim_student.c.last_name.label('last_name'),
            fact_asmt_outcome_vw.c.state_code.label('state_code'),
            fact_asmt_outcome_vw.c.enrl_grade.label('enrollment_grade'),
            fact_asmt_outcome_vw.c.asmt_grade.label('asmt_grade'),
            dim_asmt.c.asmt_subject.label('asmt_subject'),
            fact_asmt_outcome_vw.c.date_taken.label('date_taken'),
            fact_asmt_outcome_vw.c.asmt_score.label('asmt_score'),
            fact_asmt_outcome_vw.c.asmt_score_range_min.label('asmt_score_range_min'),
            fact_asmt_outcome_vw.c.asmt_score_range_max.label('asmt_score_range_max'),
            fact_asmt_outcome_vw.c.asmt_perf_lvl.label('asmt_perf_lvl'),
            dim_asmt.c.asmt_type.label('asmt_type'),
            dim_asmt.c.asmt_score_min.label('asmt_score_min'),
            dim_asmt.c.asmt_score_max.label('asmt_score_max'),
            dim_asmt.c.asmt_claim_1_name.label('asmt_claim_1_name'),
            dim_asmt.c.asmt_claim_2_name.label('asmt_claim_2_name'),
            dim_asmt.c.asmt_claim_3_name.label('asmt_claim_3_name'),
            dim_asmt.c.asmt_claim_4_name.label('asmt_claim_4_name'),
            dim_asmt.c.asmt_perf_lvl_name_1.label("asmt_cut_point_name_1"),
            dim_asmt.c.asmt_perf_lvl_name_2.label("asmt_cut_point_name_2"),
            dim_asmt.c.asmt_perf_lvl_name_3.label("asmt_cut_point_name_3"),
            dim_asmt.c.asmt_perf_lvl_name_4.label("asmt_cut_point_name_4"),
            dim_asmt.c.asmt_perf_lvl_name_5.label("asmt_cut_point_name_5"),
            dim_asmt.c.asmt_cut_point_1.label("asmt_cut_point_1"),
            dim_asmt.c.asmt_cut_point_2.label("asmt_cut_point_2"),
            dim_asmt.c.asmt_cut_point_3.label("asmt_cut_point_3"),
            dim_asmt.c.asmt_cut_point_4.label("asmt_cut_point_4"),
            fact_asmt_outcome_vw.c.asmt_claim_1_score.label('asmt_claim_1_score'),
            fact_asmt_outcome_vw.c.asmt_claim_2_score.label('asmt_claim_2_score'),
            fact_asmt_outcome_vw.c.asmt_claim_3_score.label('asmt_claim_3_score'),
            fact_asmt_outcome_vw.c.asmt_claim_4_score.label('asmt_claim_4_score'),
            fact_asmt_outcome_vw.c.asmt_claim_1_score_range_min.label('asmt_claim_1_score_range_min'),
            fact_asmt_outcome_vw.c.asmt_claim_2_score_range_min.label('asmt_claim_2_score_range_min'),
            fact_asmt_outcome_vw.c.asmt_claim_3_score_range_min.label('asmt_claim_3_score_range_min'),
            fact_asmt_outcome_vw.c.asmt_claim_4_score_range_min.label('asmt_claim_4_score_range_min'),
            fact_asmt_outcome_vw.c.asmt_claim_1_score_range_max.label('asmt_claim_1_score_range_max'),
            fact_asmt_outcome_vw.c.asmt_claim_2_score_range_max.label('asmt_claim_2_score_range_max'),
            fact_asmt_outcome_vw.c.asmt_claim_3_score_range_max.label('asmt_claim_3_score_range_max'),
            fact_asmt_outcome_vw.c.asmt_claim_4_score_range_max.label('asmt_claim_4_score_range_max'),
            # demographic information
            fact_asmt_outcome_vw.c.dmg_eth_derived.label('dmg_eth_derived'),
            fact_asmt_outcome_vw.c.dmg_prg_iep.label('dmg_prg_iep'),
            fact_asmt_outcome_vw.c.dmg_prg_lep.label('dmg_prg_lep'),
            fact_asmt_outcome_vw.c.dmg_prg_504.label('dmg_prg_504'),
            fact_asmt_outcome_vw.c.dmg_sts_ecd.label('dmg_sts_ecd'),
            fact_asmt_outcome_vw.c.dmg_sts_mig.label('dmg_sts_mig'),
            fact_asmt_outcome_vw.c.sex.label('sex'),
            # grouping information
            dim_student.c.group_1_id.label('group_1_id'),
            dim_student.c.group_1_text.label('group_1_text'),
            dim_student.c.group_2_id.label('group_2_id'),
            dim_student.c.group_2_text.label('group_2_text'),
            dim_student.c.group_3_id.label('group_3_id'),
            dim_student.c.group_3_text.label('group_3_text'),
            dim_student.c.group_4_id.label('group_4_id'),
            dim_student.c.group_4_text.label('group_4_text'),
            dim_student.c.group_5_id.label('group_5_id'),
            dim_student.c.group_5_text.label('group_5_text'),
            dim_student.c.group_6_id.label('group_6_id'),
            dim_student.c.group_6_text.label('group_6_text'),
            dim_student.c.group_7_id.label('group_7_id'),
            dim_student.c.group_7_text.label('group_7_text'),
            dim_student.c.group_8_id.label('group_8_id'),
            dim_student.c.group_8_text.label('group_8_text'),
            dim_student.c.group_9_id.label('group_9_id'),
            dim_student.c.group_9_text.label('group_9_text'),
            dim_student.c.group_10_id.label('group_10_id'),
            dim_student.c.group_10_text.label('group_10_text'),
            dim_asmt.c.asmt_claim_perf_lvl_name_1.label('asmt_claim_perf_lvl_name_1'),
            dim_asmt.c.asmt_claim_perf_lvl_name_2.label('asmt_claim_perf_lvl_name_2'),
            dim_asmt.c.asmt_claim_perf_lvl_name_3.label('asmt_claim_perf_lvl_name_3'),
            fact_asmt_outcome_vw.c.asmt_claim_1_perf_lvl.label('asmt_claim_1_perf_lvl'),
            fact_asmt_outcome_vw.c.asmt_claim_2_perf_lvl.label('asmt_claim_2_perf_lvl'),
            fact_asmt_outcome_vw.c.asmt_claim_3_perf_lvl.label('asmt_claim_3_perf_lvl'),
            fact_asmt_outcome_vw.c.asmt_claim_4_perf_lvl.label('asmt_claim_4_perf_lvl'),
            fact_asmt_outcome_vw.c.administration_condition.label('administration_condition'),
            func.coalesce(fact_asmt_outcome_vw.c.complete, True).label('complete')
        ], from_obj=[
            fact_asmt_outcome_vw
            .join(dim_student, and_(fact_asmt_outcome_vw.c.student_rec_id == dim_student.c.student_rec_id))
            .join(dim_asmt, and_(dim_asmt.c.asmt_rec_id == fact_asmt_outcome_vw.c.asmt_rec_id))
        ], permission=RolesConstants.PII, state_code=stateCode)

        query = query.where(fact_asmt_outcome_vw.c.state_code == stateCode)
        query = query.where(and_(fact_asmt_outcome_vw.c.school_id == schoolId))
        query = query.where(and_(fact_asmt_outcome_vw.c.district_id == districtId))
        query = query.where(and_(fact_asmt_outcome_vw.c.asmt_year == asmtYear))
        query = query.where(and_(fact_asmt_outcome_vw.c.rec_status == Constants.CURRENT))
        query = apply_filter_to_query(query, fact_asmt_outcome_vw, dim_student, params)

        if asmtSubject is not None:
            query = query.where(and_(dim_asmt.c.asmt_subject.in_(asmtSubject)))
        if asmtGrade is not None:
            query = query.where(and_(fact_asmt_outcome_vw.c.asmt_grade == asmtGrade))
        query = query.where(and_(or_(and_(fact_asmt_outcome_vw.c.asmt_type.in_([AssessmentType.SUMMATIVE]),
                                          (or_(fact_asmt_outcome_vw.c.administration_condition == Constants.ADMINISTRATION_CONDITION_INVALID,
                                               fact_asmt_outcome_vw.c.administration_condition == null()))),
                                     and_(fact_asmt_outcome_vw.c.asmt_type.in_([AssessmentType.INTERIM_COMPREHENSIVE])),
                                     (or_(fact_asmt_outcome_vw.c.administration_condition == null(),
                                          fact_asmt_outcome_vw.c.administration_condition.in_([Constants.ADMINISTRATION_CONDITION_STANDARDIZED,
                                                                                               Constants.ADMINISTRATION_CONDITION_NON_STANDARDIZED]))))))
        query = query.order_by(dim_student.c.last_name).order_by(dim_student.c.first_name).order_by(desc(fact_asmt_outcome_vw.c.date_taken))
        return connector.get_result(query)


def __get_asmt_data(results):
    '''
    Queries dim_asmt for cutpoint and custom metadata
    '''
    asmt_data_results = {}
    for result in results:
        asmt_subject = result['asmt_subject']
        if asmt_subject not in asmt_data_results:
            '''
            keep first available for subject.
            '''
            asmt_data_result = {}
            asmt_data_result['asmt_subject'] = asmt_subject
            asmt_data_result['asmt_cut_point_name_1'] = result['asmt_cut_point_name_1']
            asmt_data_result['asmt_cut_point_name_2'] = result['asmt_cut_point_name_2']
            asmt_data_result['asmt_cut_point_name_3'] = result['asmt_cut_point_name_3']
            asmt_data_result['asmt_cut_point_name_4'] = result['asmt_cut_point_name_4']
            asmt_data_result['asmt_cut_point_name_5'] = result['asmt_cut_point_name_5']
            asmt_data_result['asmt_cut_point_1'] = result['asmt_cut_point_1']
            asmt_data_result['asmt_cut_point_2'] = result['asmt_cut_point_2']
            asmt_data_result['asmt_cut_point_3'] = result['asmt_cut_point_3']
            asmt_data_result['asmt_cut_point_4'] = result['asmt_cut_point_4']
            asmt_data_result['asmt_score_min'] = result['asmt_score_min']
            asmt_data_result['asmt_score_max'] = result['asmt_score_max']
            asmt_data_result['asmt_claim_1_name'] = result['asmt_claim_1_name']
            asmt_data_result['asmt_claim_2_name'] = result['asmt_claim_2_name']
            asmt_data_result['asmt_claim_3_name'] = result['asmt_claim_3_name']
            asmt_data_result['asmt_claim_4_name'] = result['asmt_claim_4_name']
            asmt_data_results[asmt_subject] = asmt_data_result

    return list(asmt_data_results.values())


def __format_cut_points(results, subjects_map, custom_metadata_map):
    '''
    Returns formatted cutpoints in JSON
    '''
    cutpoints = {}
    claims = {}
    for result in results:
        subject_name = subjects_map[result["asmt_subject"]]
        custom = custom_metadata_map.get(subject_name)
        # Get formatted cutpoints data
        cutpoint = get_cut_points(custom, result)
        cutpoints[subject_name] = cutpoint
        # Get formatted claims data
        claims[subject_name] = get_claims(number_of_claims=4, result=result, include_names=True)
        # Remove unnecessary data
        del(cutpoint['asmt_subject'])
    return {'cutpoints': cutpoints, 'claims': claims, Constants.BRANDING: custom_metadata_map.get(Constants.BRANDING)}


def format_assessments_fao(results, subjects_map):
    '''
    Format student assessments.
    '''

    assessments = {}
    # Formatting data for Front End
    for result in results:
        dateTaken = result['date_taken']  # e.g. 20140401
        asmtType = capwords(result['asmt_type'], ' ')  # Summative, Interim
        asmtDict = assessments.get(asmtType, {})
        studentDataByDate = {}
        studentId = result['student_id']  # e.g. student_1
        asmtList = asmtDict.get(studentId, [])

        student = {}
        student['student_id'] = studentId
        student['student_first_name'] = result['first_name']
        student['student_middle_name'] = result['middle_name']
        student['student_last_name'] = result['last_name']
        student['enrollment_grade'] = result['enrollment_grade']
        student['state_code'] = result['state_code']
        student['demographic'] = get_student_demographic(result)
        student[Constants.ROWID] = result['student_id']

        subject = subjects_map[result['asmt_subject']]
        assessment = student.get(subject, {})
        assessment['group'] = []  # for student group filter
        for i in range(1, 11):
            if result['group_{count}_id'.format(count=i)] is not None:
                assessment['group'].append(result['group_{count}_id'.format(count=i)])
        assessment['asmt_grade'] = result['asmt_grade']
        assessment['asmt_perf_lvl'] = result['asmt_perf_lvl']
        assessment['asmt_score'] = result['asmt_score']
        assessment['asmt_score_range_min'] = result['asmt_score_range_min']
        assessment['asmt_score_range_max'] = result['asmt_score_range_max']
        assessment['asmt_score_interval'] = get_overall_asmt_interval(result)
        assessment['claims'] = get_claims(number_of_claims=4, result=result, include_scores=True, include_names=False)
        assessment['administration_condition'] = result['administration_condition']
        assessment['complete'] = result['complete']

        student[subject] = assessment
        studentDataByDate[dateTaken] = student
        asmtList.append(studentDataByDate)
        asmtDict[studentId] = asmtList
        assessments[asmtType] = asmtDict
    return assessments
