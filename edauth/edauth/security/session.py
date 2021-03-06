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
Created on Feb 15, 2013

@author: tosako
'''
import json
from edauth.security.user import User


class Session:
    '''
    Simple class that holds user session information, such as
    guid, user id, name, roles, and tenant
    '''
    def __init__(self):
        self.__initialize_session()
        # leave datetime only this class, not save in session context
        self.__expiration = None
        self.__last_access = None

    # initialize all session values
    def __initialize_session(self):
        self.__session = {}
        self.__user = User()
        self.__session_id = None
        self.__session['idpSessionIndex'] = None
        self.__session['nameId'] = None

    # serialize to text
    def get_session_json_context(self):
        # Get User Info and combined the dictionary
        combined_context = self.__user.get_user_context()
        combined_context.update_session(self.__session)
        return json.dumps(combined_context)

    def __repr__(self):
        return "%s: {session: %r, user: %r}" % (self.__class__, self.__session, self.__user)

    def __str__(self):
        return "%s (%s)" % (self.get_session_id(), self.get_user())

    def get_session_id(self):
        return self.__session_id

    def get_uid(self):
        return self.__user.get_uid()

    def get_email(self):
        return self.__user.get_email()

    def get_roles(self):
        return self.__user.get_roles()

    def get_tenants(self):
        return self.__user.get_tenants()

    def get_guid(self):
        return self.__user.get_guid()

    def get_name(self):
        return self.__user.get_name()

    def get_idp_session_index(self):
        return self.__session['idpSessionIndex']

    def get_name_id(self):
        return self.__session['nameId']

    def get_last_access(self):
        return self.__last_access

    def get_expiration(self):
        return self.__expiration

    def get_user(self):
        return self.__user

    def set_session_id(self, session_id):
        '''
        @param session_id: the session id
        '''
        self.__session_id = session_id

    def set_uid(self, uid):
        '''
        @param uid: the uid
        '''
        self.__user.set_uid(uid)

    def set_email(self, email):
        '''
        @param uid: the uid
        '''
        self.__user.set_email(email)

    def set_user_context(self, context):
        self.__user.set_context(context)

    def set_guid(self, guid):
        '''
        @param guid: the user guid to set
        '''
        self.__user.set_guid(guid)

    def set_fullName(self, fullName):
        '''
        @param fullName: the full name
        '''
        self.__user.set_full_name(fullName)

    def set_lastName(self, lastName):
        '''
        @param lastName: the last name
        '''
        self.__user.set_last_name(lastName)

    def set_firstName(self, firstName):
        '''
        @param firstName: the first name
        '''
        self.__user.set_first_name(firstName)

    def set_idp_session_index(self, index):
        '''
        @param index: the idp session index
        '''
        self.__session['idpSessionIndex'] = index

    def set_name_id(self, name_id):
        '''
        @param name_id: the name id
        '''
        self.__session['nameId'] = name_id

    def set_session(self, session):
        self.__session = session
        self.__set_user(session)

    def set_expiration(self, datetime):
        self.__expiration = datetime

    def set_last_access(self, datetime):
        self.__last_access = datetime

    def __set_user(self, info):
        self.__user.set_user_info(info)
