'''
Created on Apr 17, 2013

@author: dip
'''
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPOk, HTTPServerError
from sqlalchemy.sql.expression import select
from smarter.database import get_data_source_names
from database.connector import DBConnection
from services.tasks.pdf import health_check


@view_config(route_name='heartbeat', permission=NO_PERMISSION_REQUIRED, request_method='GET')
def heartbeat(request):
    check_list = [check_datasource, check_celery]
    results = [check_task(request) for check_task in check_list]
    results = map(lambda x: isinstance(x, HTTPServerError().__class__), results)
    if True in results:
        return HTTPServerError()
    else:
        return HTTPOk()


def check_celery(request):
    '''
    GET request that executes a task via celery and retrieve result to verify celery service
    is functioning

    :param request:  Pyramid request object
    '''
    try:
        celery_response = health_check.delay()
        heartbeat_message = celery_response.get()
    except Exception:
        heartbeat_message = 'heartattack'

    if heartbeat_message[0:9] == 'heartbeat':
        return HTTPOk()
    else:
        return HTTPServerError()


def check_datasource(request):
    '''
    GET request that executes a Select 1 and returns status of 200 if database returns results

    :param request:  Pyramid request object
    '''
    try:
        results = None
        for datasource_name in get_data_source_names():
            with DBConnection(name=datasource_name) as connector:
                query = select([1])
                results = connector.get_result(query)
    except Exception:
        results = None

    if results and len(results) > 0:
        return HTTPOk()
    return HTTPServerError()
