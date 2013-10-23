"""
Created on Oct 17, 2013

Module to initialize sftp zones and creating groups
"""

__author__ = 'sravi'

import argparse
from src.configure_sftp_zone import initialize as sftp_zone_init, cleanup as sftp_zone_cleanup
from src.configure_sftp_groups import initialize as sftp_groups_init, cleanup as sftp_groups_cleanup
from src.initialize_sftp_tenant import create_tenant, remove_tenant
from src.initialize_sftp_user import create_sftp_user, delete_user
from src.sftp_config import sftp_conf


if __name__ == "__main__":
    """
    Driver script to build and maintain sftp machine
    This script needs to be run as root user
    """
    parser = argparse.ArgumentParser(description='Process sftp driver args')
    parser.add_argument('--init', dest='driver_init_action', action='store_true')
    parser.add_argument('--cleanup', dest='driver_cleanup_action', action='store_true')
    parser.add_argument('-a', '--add_user', action='store_true', help='create the given username')
    parser.add_argument('-s', '--add_tenant', action='store_true', help='create the given tenant name')
    parser.add_argument('-u', '--username', help='The username to add')
    parser.add_argument('-t', '--tenant_name', help='The tenant name to use')
    parser.add_argument('-r', '--role_name', help='The role that the user should have')
    parser.add_argument('--remove-user', action='store_true', help='Delete the user defined by the -u option')
    parser.add_argument('--remove-tenant', action='store_true', help='Remove the tenant specified by the -t option')
    args = parser.parse_args()

    if args.driver_init_action:
        sftp_zone_init(sftp_conf)
        sftp_groups_init(sftp_conf)
    elif args.driver_cleanup_action:
        sftp_groups_cleanup(sftp_conf)
        sftp_zone_cleanup(sftp_conf)
    elif args.add_tenant:
        if args.tenant_name is None:
            parser.error('Tenant name is required to add a new tenant')
        create_tenant(args.tenant_name, sftp_conf)
    elif args.add_user:
        if args.username is None or args.tenant_name is None or args.role_name is None:
            parser.error('Username (-u), tenant name (-t) and role name (-r) are required to add a new user (-a)')
        create_sftp_user(args.tenant_name, args.username, args.role_name, sftp_conf)
    elif args.remove_user:
        if args.username is None:
            parser.error('Must specify a username (-u) to delete a user')
        delete_user(args.username)
    elif args.remove_tenant:
        if args.tenant_name is None:
            parser.error("Must specify a tenant name (-t) to delete a tenant")
        remove_tenant(args.tenant_name, sftp_conf)
    else:
        parser.error('Please specify a valid argument')
