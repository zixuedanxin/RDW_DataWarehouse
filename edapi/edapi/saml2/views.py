from pyramid.security import NO_PERMISSION_REQUIRED, forget
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config, forbidden_view_config
from edapi.saml2.saml_request import get_auth_request
'''
Created on Feb 13, 2013

@author: dip
'''


@view_config(route_name='login', permission=NO_PERMISSION_REQUIRED)
#TODO for accessign a view that user aren't allowed to do
@forbidden_view_config(renderer='json')
def login(request):
    url = 'http://edwappsrv4.poc.dum.edwdc.net:18080/opensso/SSORedirect/metaAlias/idp?%s'
    params = get_auth_request()
    return HTTPFound(location=url % params)


@view_config(route_name='logout')
def logout(request):
    # remove cookie
    headers = forget(request)
    return HTTPFound(location=request.route_url('login'), headers=headers)


@view_config(route_name='saml2_post_consumer', renderer='json', permission=NO_PERMISSION_REQUIRED)
def saml2_post_consumer(request):
    return {"Hello": "Dip"}
