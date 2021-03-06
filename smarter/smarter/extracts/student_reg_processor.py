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

__author__ = 'ablum'

"""
This module provides methods for extracting student registration report information into archive files for the user.
"""

import logging
import os
from datetime import datetime

from pyramid.threadlocal import get_current_registry

from smarter.extracts.constants import Constants as Extract, ExtractType
from edextract.tasks.constants import Constants as TaskConstants, ExtractionDataType, QueryType
from smarter.reports.helpers.constants import Constants as EndpointConstants
from edextract.status.status import create_new_entry
from smarter.extracts import processor
from smarter.extracts import student_reg_statistics
from smarter.extracts import student_reg_completion
from edcore.utils.utils import compile_query_to_sql_text
from hpz_client.frs.file_registration import register_file
from smarter.extracts.utils import start_extract


log = logging.getLogger('smarter')


def process_extraction_request(params):
    """
    @param params: Extract request parameters

    @return:  Extract response
    """

    queue = get_current_registry().settings.get('extract.job.queue.async', TaskConstants.DEFAULT_QUEUE_NAME)
    response = {}
    extract_file = {}
    state_code = params[EndpointConstants.STATECODE]
    request_id, user, tenant = processor.get_extract_request_user_info(state_code)

    extract_type = params[Extract.EXTRACTTYPE]
    extraction_data_type = ''
    if extract_type == ExtractType.studentRegistrationStatistics:
        extraction_data_type = ExtractionDataType.SR_STATISTICS
    elif extract_type == ExtractType.studentAssessmentCompletion:
        extraction_data_type = ExtractionDataType.SR_COMPLETION

    extract_params = {TaskConstants.STATE_CODE: state_code,
                      TaskConstants.ACADEMIC_YEAR: params[EndpointConstants.ACADEMIC_YEAR],
                      Extract.REPORT_TYPE: extract_type,
                      TaskConstants.EXTRACTION_DATA_TYPE: extraction_data_type}

    task_response = {TaskConstants.STATE_CODE: extract_params[TaskConstants.STATE_CODE],
                     TaskConstants.ACADEMIC_YEAR: extract_params[TaskConstants.ACADEMIC_YEAR],
                     Extract.EXTRACTTYPE: extract_params[Extract.REPORT_TYPE],
                     Extract.REQUESTID: request_id,
                     Extract.STATUS: Extract.OK}

    task_info = _create_task_info(request_id, user, tenant, extract_params)

    response['tasks'] = [task_response]

    archived_file_path = processor.get_archive_file_path(user.get_uid(), tenant, request_id)
    extract_file['fileName'] = os.path.basename(archived_file_path)

    data_directory_to_archive = processor.get_extract_work_zone_path(tenant, request_id)

    # Register extract file with HPZ.
    registration_id, download_url, web_download_url = register_file(user.get_uid(), user.get_email())
    extract_file[EndpointConstants.DOWNLOAD_URL] = download_url
    extract_file[EndpointConstants.WEB_DOWNLOAD_URL] = web_download_url
    response[EndpointConstants.FILES] = [extract_file]

    start_extract(tenant, request_id, [archived_file_path], [data_directory_to_archive], [registration_id], [task_info], queue=queue)

    return response


def _create_task_info(request_id, user, tenant, extract_params):

    task_info = {TaskConstants.TASK_TASK_ID: create_new_entry(user, request_id, extract_params),
                 TaskConstants.TASK_FILE_NAME: _get_extract_file_path(request_id, tenant, extract_params),
                 TaskConstants.CSV_HEADERS: __get_report_headers(extract_params),
                 TaskConstants.TASK_QUERIES: __get_report_queries(extract_params)}
    task_info.update(extract_params)

    return task_info


def __get_report_headers(extract_params):
    extract_type = extract_params[Extract.REPORT_TYPE]
    headers = ()

    if extract_type == ExtractType.studentRegistrationStatistics:
        headers = student_reg_statistics.get_headers(extract_params.get(TaskConstants.ACADEMIC_YEAR))
    if extract_type == ExtractType.studentAssessmentCompletion:
        headers = student_reg_completion.get_headers(extract_params.get(TaskConstants.ACADEMIC_YEAR))

    return headers


def __get_report_queries(extract_params):
    extract_type = extract_params[Extract.REPORT_TYPE]
    queries = {}

    if extract_type == ExtractType.studentRegistrationStatistics:
        academic_year_query = student_reg_statistics.get_academic_year_query(extract_params[TaskConstants.ACADEMIC_YEAR],
                                                                             extract_params[TaskConstants.STATE_CODE])
        match_id_query = student_reg_statistics.get_match_id_query(extract_params[TaskConstants.ACADEMIC_YEAR],
                                                                   extract_params[TaskConstants.STATE_CODE])

        queries = {QueryType.QUERY: compile_query_to_sql_text(academic_year_query),
                   QueryType.MATCH_ID_QUERY: compile_query_to_sql_text(match_id_query)}
    elif extract_type == ExtractType.studentAssessmentCompletion:
        registered_query = student_reg_completion.get_academic_year_query(extract_params[TaskConstants.ACADEMIC_YEAR],
                                                                          extract_params[TaskConstants.STATE_CODE])
        asmt_query = student_reg_completion.get_assessment_query(extract_params[TaskConstants.ACADEMIC_YEAR],
                                                                 extract_params[TaskConstants.STATE_CODE])

        queries = {QueryType.QUERY: compile_query_to_sql_text(registered_query),
                   QueryType.ASMT_OUTCOME_QUERY: compile_query_to_sql_text(asmt_query)}

    return queries


def _get_extract_file_path(request_id, tenant, params):
    file_name = '{stateCode}_{academicYear}_{reportType}_{currentTime}.csv'.format(stateCode=params.get(TaskConstants.STATE_CODE),
                                                                                   academicYear=params.get(TaskConstants.ACADEMIC_YEAR),
                                                                                   reportType=params.get(Extract.REPORT_TYPE),
                                                                                   currentTime=str(datetime.now().strftime("%m-%d-%Y_%H-%M-%S")))

    return os.path.join(processor.get_extract_work_zone_path(tenant, request_id), file_name)
