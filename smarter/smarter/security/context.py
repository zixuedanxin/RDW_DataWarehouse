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
Created on May 7, 2013

@author: dip
'''
from functools import wraps
from sqlalchemy.sql.expression import Select
from pyramid.security import authenticated_userid
import pyramid
from pyramid.httpexceptions import HTTPForbidden
from smarter.reports.helpers.constants import Constants
from smarter.security.context_role_map import ContextRoleMap
from edcore.database.edcore_connector import EdCoreDBConnection
from edcore.security.tenant import get_tenant_by_state_code
from smarter_common.security.constants import RolesConstants


def select_with_context(columns=None, whereclause=None, from_obj=[], permission=RolesConstants.PII, **kwargs):
    '''
    Returns a SELECT clause statement with context security attached in the WHERE clause

    Note: state_code must be passed in as kwargs for database routing for multi tenant users
    '''
    # Retrieve state code for db connection routing
    state_code = kwargs.get(Constants.STATE_CODE)
    kwargs.pop(Constants.STATE_CODE, None)
    with EdCoreDBConnection(state_code=state_code) as connector:
        # Get user role and guid
        user = __get_user_info()

        # Build query
        query = Select(columns, whereclause=whereclause, from_obj=from_obj, **kwargs)

        if permission not in user.get_roles():
            raise HTTPForbidden()
        context = __get_context_instance(permission, connector)
        # Get context security expression to attach to where clause
        query = context.add_context(get_tenant_by_state_code(state_code), user, query)

    return query


def check_context(permission, state_code, student_ids):
    '''
    Given a list of student guids, return true if user has access to see their data, false otherwise

    :param student_ids: guids of students that we want to check whether the user has context to
    :type student_ids: list
    '''
    if not student_ids:
        return False

    with EdCoreDBConnection(state_code=state_code) as connector:
        # Get user role and guid
        user = __get_user_info()
        context = __get_context_instance(permission, connector)
        return context.check_context(get_tenant_by_state_code(state_code), user, student_ids)


def get_current_context(params):
    '''
    Given request parameters, determine if the user has context to the next hierarchy level
    '''
    user = __get_user_info()
    state_code = params.get(Constants.STATECODE)
    tenant = get_tenant_by_state_code(state_code)
    # This is for defaults - used in public reports
    pii = {'all': False} if params.get(Constants.SCHOOLGUID) else {'all': True}
    sar_extracts = False
    srs_extracts = False
    src_extracts = False
    audit_xml_extracts = False
    item_lvl_extracts = False
    if user is not None:
        user_context = user.get_context()
        # Special case for pii
        pii = user_context.get_chain(tenant, RolesConstants.PII, params) if params.get(Constants.SCHOOLGUID) else {'all': True}
        sar_extracts = user_context.get_chain(tenant, RolesConstants.SAR_EXTRACTS, params)
        srs_extracts = user_context.get_chain(tenant, RolesConstants.SRS_EXTRACTS, params)
        src_extracts = user_context.get_chain(tenant, RolesConstants.SRC_EXTRACTS, params)
        audit_xml_extracts = user_context.get_chain(tenant, RolesConstants.AUDIT_XML_EXTRACTS, params)
        item_lvl_extracts = user_context.get_chain(tenant, RolesConstants.ITEM_LEVEL_EXTRACTS, params)
    return {'pii': pii, 'sar_extracts': sar_extracts, 'srs_extracts': srs_extracts, 'src_extracts': src_extracts, 'audit_xml_extracts': audit_xml_extracts, 'item_extracts': item_lvl_extracts}


def get_user_context_for_role(tenant, role, req_params):
    '''
    return user context relationships for a particular role and tenant
    @tenant - tenant the user requested
    @role - a user role to get context for
    @req_params - request params to infer state from
    '''
    user_context = __get_user_info().get_context()
    state_code = req_params.get(Constants.STATECODE)
    params = {Constants.STATECODE: state_code}
    districts = []

    context = user_context.get_chain(tenant, role, params)
    if context['all']:
        return districts
    context_districts = context[Constants.GUID]
    if context_districts:
        for district_id in context_districts:
            params = {Constants.STATECODE: state_code, Constants.DISTRICTGUID: district_id}
            params.update({'guid': user_context.get_chain(tenant, role, params)['guid']})
            districts.append({'params': params})
    return districts


def get_current_request_context(origin_func):
    '''
    Decorator to return current user context
    '''
    @wraps(origin_func)
    def wrap(*args, **kwds):
        results = origin_func(*args, **kwds)
        if results:
            results['context']['permissions'] = get_current_context(*args)
        return results
    return wrap


def __get_user_info():
    '''
    Returns user object.  This is not the session object

    '''
    return authenticated_userid(pyramid.threadlocal.get_current_request())


def __get_context_instance(role, connector):
    '''
    Given a role in string, return the context instance for it
    '''
    # Get the context object
    context_obj = ContextRoleMap.get_context(role)
    # Instantiate it
    return context_obj(connector, role)
