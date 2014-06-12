'''
Created on May 17, 2013

@author: dip
'''
from pyramid.view import view_config
from services.tasks.pdf import prepare, pdf_merge, get, archive, hpz_upload_cleanup
from urllib.parse import urljoin
from pyramid.response import Response
from smarter.security.context import check_context
from edapi.exceptions import InvalidParameterError, ForbiddenError
from edauth.security.utils import get_session_cookie
import urllib.parse
import pyramid.threadlocal
from sqlalchemy.sql import select
from sqlalchemy.sql import and_
from edcore.database.edcore_connector import EdCoreDBConnection
from smarter.security.context import select_with_context
from smarter.reports.helpers.filters import apply_filter_to_query
from edapi.httpexceptions import EdApiHTTPPreconditionFailed, \
    EdApiHTTPForbiddenAccess, EdApiHTTPInternalServerError
from services.exceptions import PdfGenerationError
from smarter.reports.helpers.ISR_pdf_name_formatter import generate_isr_report_path_by_student_guid
from smarter.reports.helpers.constants import AssessmentType, Constants
import services.celery
from edapi.decorators import validate_params
from edcore.utils.utils import to_bool
from smarter.security.constants import RolesConstants
from hpz_client.frs.file_registration import register_file
from celery.canvas import group, chain
from pyramid.security import authenticated_userid
from pyramid.threadlocal import get_current_request
import copy
from datetime import datetime
import json
import os

PDF_PARAMS = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        Constants.STATECODE: {
            "type": "string",
            "required": True,
            "pattern": "^[a-zA-Z]{2}$"},
        Constants.STUDENTGUID: {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^[a-zA-Z0-9\-]{0,50}$"
            },
            "minItems": 1,
            "uniqueItems": True,
            "required": False},
        Constants.DISTRICTGUID: {
            "type": "string",
            "required": False,
            "pattern": "^[a-zA-Z0-9 ]{0,50}$",
        },
        Constants.SCHOOLGUID: {
            "type": "string",
            "required": False,
            "pattern": "^[a-zA-Z0-9 ]{0,50}$",
        },
        Constants.ASMTGRADE: {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^[0-9 ]{0,2}$"
            },
            "minitems": 1,
            "uniqueItems": True,
            "required": False
        },
        Constants.ASMTTYPE: {
            "type": "string",
            "required": False,
            "pattern": "^[a-zA-Z0-9 ]{0,50}$",
        },
        Constants.GRAYSCALE: {
            "type": "string",
            "required": False,
            "pattern": "^(true|false|TRUE|FALSE)$",
        },
        Constants.LANG: {
            "type": "string",
            "required": False,
            "pattern": "^[a-z]{2}$",
        },
        Constants.PDF: {
            "type": "string",
            "required": False,
            "pattern": "^(true|false|TRUE|FALSE)$",
        },
        Constants.SL: {
            "type": "string",
            "required": False,
            "pattern": "^\d+$",
        },
        Constants.EFFECTIVEDATE: {
            "type": "integer",
            "required": True,
            "pattern": "^[1-9]{8}$"
        }
    }
}


@view_config(route_name='pdf', request_method='POST', content_type='application/json')
@validate_params(schema=PDF_PARAMS)
def post_pdf_service(context, request):
    '''
    Handles POST request to /services/pdf

    :param request:  Pyramid request object
    '''
    try:
        params = request.json_body
    except ValueError:
        raise EdApiHTTPPreconditionFailed('Payload cannot be parsed')

    return send_pdf_request(params)


@view_config(route_name='pdf', request_method='GET')
@validate_params(schema=PDF_PARAMS)
def get_pdf_service(context, request):
    '''
    Handles GET request to /services/pdf

    :param request:  Pyramid request object
    '''
    return send_pdf_request(request.GET)


def send_pdf_request(params):
    '''
    Requests for pdf content, throws http exceptions when error occurs

    :param params: python dict that contains query parameters from the request
    '''
    try:
        response = get_pdf_content(params)
    except InvalidParameterError as e:
        raise EdApiHTTPPreconditionFailed(e.msg)
    except ForbiddenError as e:
        raise EdApiHTTPForbiddenAccess(e.msg)
    except (PdfGenerationError, TimeoutError) as e:
        raise EdApiHTTPInternalServerError(e.msg)
    except Exception as e:
        # if celery get task got timed out...
        raise EdApiHTTPInternalServerError("Internal Error")

    return response


def get_pdf_content(params):
    '''
    Read pdf content from file system if it exists, else generate it

    :param params: python dict that contains query parameters from the request
    '''
    # Get the user
    user = authenticated_userid(get_current_request())

    # Collect the parameters
    student_guids = params.get(Constants.STUDENTGUID)
    state_code = params.get(Constants.STATECODE)
    district_guid = params.get(Constants.DISTRICTGUID)
    school_guid = params.get(Constants.SCHOOLGUID)
    grades = params.get(Constants.ASMTGRADE, [])
    asmt_type = params.get(Constants.ASMTTYPE, AssessmentType.SUMMATIVE)
    effective_date = str(params.get(Constants.EFFECTIVEDATE))
    is_grayscale = bool(params.get('grayscale', 'false').lower() == 'true')
    lang = params.get('lang', 'en').lower()

    # Check that we have either a list of student GUIDs or a district/school/grade combination in the params
    if student_guids is None and (district_guid is None or school_guid is None or grades is None):
        raise InvalidParameterError('Required parameter is missing')

    # Validate the assessment type
    asmt_type = asmt_type.upper()
    if asmt_type not in [AssessmentType.SUMMATIVE, AssessmentType.INTERIM_COMPREHENSIVE]:
        raise InvalidParameterError('Unknown assessment type')

    # Get cookies and other config items
    (cookie_name, cookie_value) = get_session_cookie()
    celery_timeout = int(pyramid.threadlocal.get_current_registry().settings.get('pdf.celery_timeout', '30'))
    always_generate = to_bool(pyramid.threadlocal.get_current_registry().settings.get('pdf.always_generate', False))

    # Verify student GUIDs is a list (if we have them)
    if student_guids is not None and type(student_guids) is not list:
        student_guids = [student_guids]

    # Set the base individual PDF generation URL
    base_url = urljoin(pyramid.threadlocal.get_current_request().application_url,
                       '/assets/html/indivstudentreport.html')

    # If we do not have a list of student GUIDs, we need to get it
    all_guids = []
    guids_by_grade = {}
    if student_guids is None:
        for grade in grades:
            guids = _get_student_guids(state_code, district_guid, school_guid, grade, asmt_type, effective_date, params)
            all_guids.extend([result['student_guid'] for result in guids])
            guids_by_grade[grade] = [result['student_guid'] for result in guids]
    else:
        all_guids.extend(student_guids)
        guids_by_grade['all'] = student_guids

    # Set up a few additional variables
    pdf_base_dir = pyramid.threadlocal.get_current_registry().settings.get('pdf.report_base_dir', "/tmp")
    urls_by_guid = {}

    # Get all file names
    files_by_guid = generate_isr_report_path_by_student_guid(state_code, effective_date,
                                                             pdf_report_base_dir=pdf_base_dir, student_guids=all_guids,
                                                             asmt_type=asmt_type, grayScale=is_grayscale, lang=lang)

    # Work through each grade
    for _, guids in guids_by_grade.items():
        # Create URLs
        for student_guid in guids:
            # Check if the user has access to PII for all of these students
            if not _has_context_for_pdf_request(state_code, student_guid):
                raise ForbiddenError('Access Denied')
            urls_by_guid[student_guid] = _create_student_pdf_url(student_guid, base_url, params)

    # Decide if this is a bulk merge or simple PDF return
    if len(urls_by_guid) > 1:
        # Register expected file with HPZ
        registration_id, download_url = register_file(user.get_uid())

        school_name = 'Example School'  # TODO: Get from somewhere
        # Set up directory and file names
        archive_file_name = _get_archive_name(os.path.join(pdf_base_dir, 'bulk', registration_id, 'zip'),
                                              school_name, lang, is_grayscale)
        directory_to_archive = os.path.join(pdf_base_dir, 'bulk', registration_id, 'data')

        # Create JSON response
        response = {'fileName': archive_file_name, 'download_url': download_url}

        # Create the tasks for each individual student PDF file we want to merge
        generate_tasks = []
        args = {'cookie': cookie_value, 'timeout': services.celery.TIMEOUT, 'cookie_name': cookie_name,
                'grayscale': is_grayscale, 'always_generate': always_generate}
        for guid, file_name in files_by_guid.items():
            copied_args = copy.deepcopy(args)
            copied_args['url'] = urls_by_guid[guid]
            copied_args['outputfile'] = file_name
            generate_tasks.append(prepare.subtask(kwargs=copied_args, immutable=True))  # @UndefinedVariable

        # Create the tasks to merge each PDF by grade
        merge_tasks = []
        for grade, guids in guids_by_grade.items():
            # Create bulk output name
            bulk_name = _get_merged_pdf_name(directory_to_archive, 'Example School', grade, lang, is_grayscale)

            # Get the files for this grade
            file_names = []
            for student_guid in guids:
                file_names.append(files_by_guid[student_guid])

            # Create the merge task
            merge_tasks.append(pdf_merge.subtask(args=(file_names, bulk_name, pdf_base_dir, services.celery.TIMEOUT),
                                                 immutable=True))

        # Start the bulk merge
        _start_bulk(archive_file_name, directory_to_archive, registration_id, generate_tasks, merge_tasks, pdf_base_dir)

        # Return the JSON response while the bulk merge runs asynchronously
        return Response(body=json.dumps(response), content_type='application/json')
    else:
        # Get the URL and file name
        url = urls_by_guid[all_guids[0]]
        file_name = files_by_guid[all_guids[0]]

        # Create the task and stream the individual PDF response back to the browser
        celery_response = get.delay(cookie_value, url, file_name, cookie_name=cookie_name,
                                    timeout=services.celery.TIMEOUT, grayscale=is_grayscale,
                                    always_generate=always_generate)
        pdf_stream = celery_response.get(timeout=celery_timeout)
        return Response(body=pdf_stream, content_type='application/pdf')


def _has_context_for_pdf_request(state_code, student_guid):
    '''
    Validates that user has context to student_guid

    :param student_guid:  guid(s) of the student(s)
    '''
    if type(student_guid) is not list:
        student_guid = [student_guid]
    return check_context(RolesConstants.PII, state_code, student_guid)


def _create_student_pdf_url(student_guid, base_url, params):
    params[Constants.STUDENTGUID] = student_guid
    encoded_params = urllib.parse.urlencode(params)
    return base_url + "?%s" % encoded_params


def _start_bulk(archive_file_name, directory_to_archive, registration_id, gen_tasks, merge_tasks, pdf_base_dir):
    '''
    entry point to start a bulk PDF generation request for one or more students
    it groups the generation of individual PDFs into a celery task group and then chains it to the next task to merge
    the files into one PDF, archive the PDF into a zip, and upload the zip to HPZ
    '''

    workflow = chain(group(gen_tasks),
                     group(merge_tasks),
                     archive.subtask(args=(archive_file_name, directory_to_archive), immutable=True),
                     hpz_upload_cleanup.subtask(args=(archive_file_name, registration_id, pdf_base_dir),
                                                immutable=True))
    workflow.apply_async()


def _get_merged_pdf_name(out_dir, school_name, grade, lang_code, grayscale):
    timestamp = str(datetime.now().strftime("%m-%d-%Y_%H-%M-%S"))
    school_name = school_name.replace(' ', '')
    school_name = school_name[:15] if len(school_name) > 15 else school_name
    name = 'student_reports_{school_name}_grade_{grade}_{timestamp}_{lang}'.format(school_name=school_name,
                                                                                   grade=grade,
                                                                                   timestamp=timestamp,
                                                                                   lang=lang_code.lower())
    return os.path.join(out_dir, name + ('.g.pdf' if grayscale else '.pdf'))


def _get_archive_name(out_dir, school_name, lang_code, grayscale):
    timestamp = str(datetime.now().strftime("%m-%d-%Y_%H-%M-%S"))
    school_name = school_name.replace(' ', '')
    school_name = school_name[:15] if len(school_name) > 15 else school_name
    name = 'student_reports_{school_name}_{timestamp}_{lang}'.format(school_name=school_name,
                                                                     timestamp=timestamp,
                                                                     lang=lang_code.lower())
    return os.path.join(out_dir, name + ('.g.zip' if grayscale else '.zip'))


def _get_student_guids(stateCode, districtGuid, schoolGuid, grade, asmtType, effectiveDate, params):
    with EdCoreDBConnection(state_code=stateCode) as connector:
        # Get handle to tables
        dim_student = connector.get_table(Constants.DIM_STUDENT)
        dim_asmt = connector.get_table(Constants.DIM_ASMT)
        fact_asmt_outcome_vw = connector.get_table(Constants.FACT_ASMT_OUTCOME_VW)

        # Build select
        query = select_with_context([fact_asmt_outcome_vw.c.student_guid,
                                     dim_student.c.first_name,
                                     dim_student.c.last_name],
                                    from_obj=[fact_asmt_outcome_vw
                                              .join(dim_student, and_(fact_asmt_outcome_vw.c.student_rec_id == dim_student.c.student_rec_id))
                                              .join(dim_asmt, and_(dim_asmt.c.asmt_rec_id == fact_asmt_outcome_vw.c.asmt_rec_id))],
                                    permission=RolesConstants.PII, state_code=stateCode).distinct()

        # Add where clauses
        query = query.where(fact_asmt_outcome_vw.c.state_code == stateCode)
        query = query.where(and_(fact_asmt_outcome_vw.c.school_guid == schoolGuid))
        query = query.where(and_(fact_asmt_outcome_vw.c.district_guid == districtGuid))
        query = query.where(and_(fact_asmt_outcome_vw.c.enrl_grade == grade))
        query = query.where(and_(fact_asmt_outcome_vw.c.rec_status == Constants.CURRENT))
        query = query.where(and_(fact_asmt_outcome_vw.c.asmt_type == asmtType))
        query = query.where(and_(dim_asmt.c.effective_date == effectiveDate))
        query = apply_filter_to_query(query, fact_asmt_outcome_vw, params)

        # Add order by clause
        query = query.order_by(dim_student.c.last_name).order_by(dim_student.c.first_name)

        # Return the result
        return connector.get_result(query)
