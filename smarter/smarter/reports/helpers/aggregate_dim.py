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
Created on May 12, 2014

@author: agrebneva
'''
from sqlalchemy.sql import select, and_, exists
from smarter.reports.helpers.constants import Constants, AssessmentType
from sqlalchemy.sql.expression import distinct
from edapi.cache import cache_region
from copy import deepcopy
from edcore.database.routing import ReportingDbConnection

CACHE_REGION_PUBLIC_SHORTLIVED = 'public.shortlived'


def get_aggregate_dim_interim(stateCode=None, districtId=None, schoolId=None, asmtYear=None, tenant=None, subjects={}, is_public=False, **args):
    records = {}
    for subject_key in subjects.keys():
        subject = subjects[subject_key]
        rows = _get_aggregate_dim_for_interim(stateCode, districtId, schoolId, asmtYear, tenant, subject_key, subject, is_public)
        for key in rows.keys():
            record = records.get(key)
            if record is None:
                records[key] = deepcopy(rows[key])
            else:
                record[Constants.RESULTS][subject_key] = deepcopy(rows[key][Constants.RESULTS][subject_key])
    sorted_records = sorted(list(records.values()), key=lambda k: k['name'])
    for subject_key in subjects.keys():
        for sorted_record in sorted_records:
            results = sorted_record[Constants.RESULTS]
            if results.get(subject_key) is None:
                results[subject_key] = {Constants.ASMT_SUBJECT: subjects[subject_key], Constants.TOTAL: 0, Constants.HASINTERIM: False}
    return {Constants.RECORDS: sorted_records}


def get_aggregate_dim_cache_route(stateCode, districtId, schoolId, asmtYear, tenant, subject_key, subject, *args, **kwargs):
    '''
    If school_id is present, return none - do not cache
    '''
    if schoolId is not None:
        return None  # do not cache school level
    return 'public.shortlived'


def get_aggregate_dim_cache_route_cache_key(stateCode, districtId, schoolId, asmtYear, tenant, subject_key, subject, is_public, *args, **kwargs):
    '''
    Returns cache key for get_aggregate_dim

    :param comparing_pop:  instance of ComparingPopReport
    :returns: a tuple representing a unique key for comparing populations report
    '''
    cache_args = []
    if stateCode is not None:
        cache_args.append(stateCode)
    if districtId is not None:
        cache_args.append(districtId)
    cache_args.append(asmtYear)
    cache_args.append(subject)
    cache_args.append(is_public)
    return tuple(cache_args)


@cache_region([CACHE_REGION_PUBLIC_SHORTLIVED], router=get_aggregate_dim_cache_route, key_generator=get_aggregate_dim_cache_route_cache_key)
def _get_aggregate_dim_for_interim(stateCode=None, districtId=None, schoolId=None, asmtYear=None, tenant=None, subject_key=None, subject=None, is_public=False):
    '''
    Query for institution or grades that have asmts for the year provided
    :param string stateCode
    :param string districtId
    :param string schoolId
    :param string asmtType
    :param string asmtYear
    :param string tenant: tenant info for database connection
    :rtype: rset
    :returns: set of records with district guids
    '''
    def create_where_clause(fact_table, asmt):
        where = and_(fact_table.c.asmt_year == asmtYear, fact_table.c.state_code == stateCode, fact_table.c.rec_status == 'C',
                     fact_table.c.asmt_type == asmt, fact_table.c.inst_hier_rec_id == dim_inst_hier.c.inst_hier_rec_id,
                     fact_table.c.asmt_subject == subject)
        return where
    rows = {}
    with ReportingDbConnection(tenant=tenant, state_code=stateCode, is_public=is_public) as connector:
        # query custom metadata by state code
        dim_inst_hier = connector.get_table(Constants.DIM_INST_HIER)
        fact_asmt_outcome = connector.get_table(Constants.FACT_ASMT_OUTCOME_VW)
        fact_block_asmt_outcome = connector.get_table(Constants.FACT_BLOCK_ASMT_OUTCOME)
        s_fao = exists(['*'], from_obj=[dim_inst_hier]).where(create_where_clause(fact_asmt_outcome, AssessmentType.INTERIM_COMPREHENSIVE))
        s_fbao = exists(['*'], from_obj=[dim_inst_hier]).where(create_where_clause(fact_block_asmt_outcome, AssessmentType.INTERIM_ASSESSMENT_BLOCKS))
        if districtId is None and schoolId is None:
            query_fao = get_select_for_state_view(dim_inst_hier, stateCode).where(s_fao)
            query_fbao = get_select_for_state_view(dim_inst_hier, stateCode).where(s_fbao)
            query = query_fao.union(query_fbao)
        elif districtId is not None and schoolId is not None:
            fao_query = get_select_for_school_view(fact_asmt_outcome, stateCode, districtId, schoolId, asmtYear, AssessmentType.INTERIM_COMPREHENSIVE, subject)
            fbao_query = get_select_for_school_view(fact_block_asmt_outcome, stateCode, districtId, schoolId, asmtYear, AssessmentType.INTERIM_ASSESSMENT_BLOCKS, subject)
            query = fao_query.union(fbao_query)
        else:
            query_fao = get_select_for_district_view(dim_inst_hier, stateCode, districtId).where(s_fao)
            query_fbao = get_select_for_district_view(dim_inst_hier, stateCode, districtId).where(s_fbao)
            query = query_fao.union(query_fbao)
        results = connector.get_result(query)
        for result in results:
            params = {Constants.ID: result.get(Constants.ID), Constants.STATECODE: stateCode}
            if districtId is not None:
                params[Constants.DISTRICTGUID] = districtId
            if schoolId is not None:
                params[Constants.SCHOOLGUID] = schoolId
            data = {Constants.ID: result.get(Constants.ID),
                    Constants.ROWID: result.get(Constants.ID),
                    Constants.NAME: result.get(Constants.NAME),
                    Constants.PARAMS: params,
                    Constants.RESULTS: {}
                    }
            data[Constants.RESULTS][subject_key] = {Constants.ASMT_SUBJECT: subject, Constants.TOTAL: -1, Constants.HASINTERIM: True}
            rows[data[Constants.ID]] = data
    return rows


def get_select_for_state_view(dim_inst_hier, state_code):
    return select([distinct(dim_inst_hier.c.district_id).label(Constants.ID), dim_inst_hier.c.district_name.label(Constants.NAME)], from_obj=[dim_inst_hier]).where(dim_inst_hier.c.state_code == state_code)


def get_select_for_district_view(dim_inst_hier, state_code, district_id):
    return select([distinct(dim_inst_hier.c.school_id).label(Constants.ID), dim_inst_hier.c.school_name.label(Constants.NAME)], from_obj=[dim_inst_hier])\
        .where(and_(dim_inst_hier.c.state_code == state_code, dim_inst_hier.c.district_id == district_id))


def get_select_for_school_view(fact_table, state_code, district_id, school_id, asmtYear, asmtType, subject):
    return select([distinct(fact_table.c.asmt_grade).label(Constants.ID), fact_table.c.asmt_grade.label(Constants.NAME)], from_obj=[fact_table])\
        .where(and_(fact_table.c.state_code == state_code,
                    fact_table.c.district_id == district_id,
                    fact_table.c.school_id == school_id,
                    fact_table.c.asmt_year == asmtYear,
                    fact_table.c.rec_status == 'C',
                    fact_table.c.asmt_type == asmtType,
                    fact_table.c.asmt_subject == subject))
