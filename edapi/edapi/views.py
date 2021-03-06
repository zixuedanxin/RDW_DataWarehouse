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

'''
Handles requests to REST endpoints

Created on Jan 14, 2013

@author: aoren
'''
from pyramid.view import view_config
from edapi.reports import generate_report_config, EDAPI_REPORTS_PLACEHOLDER
from edapi.exceptions import ReportNotFoundError, InvalidParameterError,\
    ForbiddenError
from edapi.httpexceptions import EdApiHTTPNotFound, EdApiHTTPPreconditionFailed,\
    EdApiHTTPRequestURITooLong, EdApiHTTPForbiddenAccess
from pyramid.response import Response
import json
from edapi import reports
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.httpexceptions import HTTPMovedPermanently

MAX_REQUEST_URL_LENGTH = 2000


def get_report_registry(request, name=None):
    '''
    Given a request, return the registry belonging to edapi reports

    :param name: the report name that is trying to get the registry (will get used if the registry is not found)
    :type name: string
    '''
    reg = request.registry.get(EDAPI_REPORTS_PLACEHOLDER)
    if (reg is None):
        raise ReportNotFoundError(name)
    return reg


def get_request_body(request):
    '''
    Returns pyramid request body as json, throws exception if request.json_body isn't valid json

    :param request: the request object
    :type request: request
    '''
    try:
        body = request.json_body
    except ValueError:
        raise InvalidParameterError
    return body


@view_config(route_name='list_of_reports', renderer='json', request_method='GET')
def get_list_of_reports(request):
    '''
    Returns list of reports in GET request
    '''
    try:
        reports = get_report_registry(request)
    except ReportNotFoundError:
        return []
    return list(reports.keys())


@view_config(route_name='report_get_option_post', renderer='json', request_method='OPTIONS')
def get_report_config(request):
    '''
    Handle OPTIONS for data resource

    :param request: the request object
    :type request: request
    '''
    # gets the name of the report from the URL
    reportName = request.matchdict['name']
    # find the report configuration in the repository
    try:
        report_config = generate_report_config(get_report_registry(request, reportName), reportName)
    # if we cannot find the report configuration in the repository, we return 404 error
    except ReportNotFoundError as e:
        return EdApiHTTPNotFound(e.msg)
    return Response(body=json.dumps(report_config), content_type="application/json", allow='GET,POST,OPTIONS')


def generate_report(request, validator=None, prefix=''):
    # if full request URL with query string is too long
    if (len(request.url) > MAX_REQUEST_URL_LENGTH):
        return EdApiHTTPRequestURITooLong(MAX_REQUEST_URL_LENGTH)

    # gets the name of the report from the URL
    reportName = prefix + request.matchdict['name']

    params = request.GET.copy()

    try:
        if getattr(request, 'method', 'GET') == 'POST':
            params.update(get_request_body(request))
        report = reports.generate_report(get_report_registry(request, reportName), reportName, params, validator)
    except ReportNotFoundError as e:
        return EdApiHTTPNotFound(e.msg)
    except InvalidParameterError as e:
        return EdApiHTTPPreconditionFailed(e.msg)
    except ForbiddenError as e:
        return EdApiHTTPForbiddenAccess(e.msg)
    return report


@view_config(route_name='report_get_option_post', renderer='json', request_method='GET', content_type="application/json",)
@view_config(route_name='report_get_option_post', renderer='json', request_method='POST', content_type="application/json",)
def generate_protected_report(request, validator=None):
    '''
    Handle GET for data resource

    :param request: the request object
    :type request: request
    :param validator:
    '''
    return generate_report(request, validator=validator)


@view_config(route_name='public_report_get_option_post', renderer='json', request_method='GET', permission=NO_PERMISSION_REQUIRED, content_type="application/json",)
@view_config(route_name='public_report_get_option_post', renderer='json', request_method='POST', permission=NO_PERMISSION_REQUIRED, content_type="application/json",)
def generate_public_report(request, validator=None):
    '''
    Handles request for /public_data/{name}
    These end points do not require permissions
    '''
    return generate_report(request, validator=validator, prefix='public.')


@view_config(route_name='public_report_short_url', permission=NO_PERMISSION_REQUIRED)
def public_report_short_url(request, validator=None):
    request.matchdict['name'] = 'public_short_url'
    request.GET['sid'] = request.matchdict['sid']
    path = generate_report(request, validator, prefix='public.')
    url = request.application_url + path
    return HTTPMovedPermanently(location=url, expires=0, cache_control='no-store, no-cache, must-revalidate')
