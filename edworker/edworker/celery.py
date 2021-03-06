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
Created on May 14, 2013

@author: dip
'''
import os
from celery import Celery
from datetime import timedelta
from celery.schedules import crontab
from kombu import Queue, Exchange
from kombu.common import Broadcast
import configparser
from edworker.celeryconfig import get_config

CELERY_QUEUES = 'CELERY_QUEUES'
CELERY_ROUTES = 'CELERY_ROUTES'
CELERYBEAT_SCHEDULE = 'CELERYBEAT_SCHEDULE'
CELERY_BROADCAST_QUEUES = 'CELERY_BROADCAST_QUEUES'
CELERY_QUEUE_NAME = 'name'
CELERY_QUEUE_EXCHANGE = 'exchange'
CELERY_QUEUE_ROUTING_KEY = 'key'
CELERY_QUEUES_DURABLE = 'durable'
CELERYBEAT_SCHEDULE_NAME = 'name'
CELERYBEAT_SCHEDULE_TASK = 'task'
CELERYBEAT_SCHEDULE_SCH = 'schedule'
CELERYBEAT_SCHEDULE_HOUR = 'hour'
CELERYBEAT_SCHEDULE_MIN = 'min'
CELERYBEAT_SCHEDULE_SEC = 'seconds'
CRON = 'cron'
TIMEDELTA = 'timedelta'


def setup_celery(celery, settings, prefix='celery'):
    '''
    Setup celery based on parameters defined in setting (ini file)

    :param settings:  dict of configurations
    :param prefix: prefix in configurations used for configuring celery
    '''

    celery_config = get_config(settings, prefix)
    if celery_config.get(CELERY_QUEUES):
        real_queues = []
        for queue in celery_config.get(CELERY_QUEUES):
            real_queues.append(create_queue(queue))
        celery_config[CELERY_QUEUES] = real_queues
    if celery_config.get(CELERYBEAT_SCHEDULE):
        beat_schedules = {}
        for schedule in celery_config.get(CELERYBEAT_SCHEDULE):
            beat_schedules[schedule[CELERYBEAT_SCHEDULE_NAME]] = get_schedule(schedule)
        celery_config[CELERY_QUEUES] = real_queues
        celery_config[CELERYBEAT_SCHEDULE] = beat_schedules
    if celery_config.get(CELERY_ROUTES):
        real_routes = {}
        for route in celery_config.get(CELERY_ROUTES):
            for task, route_info in route.items():
                real_routes[task] = route_info
        celery_config[CELERY_ROUTES] = real_routes
    celery.config_from_object(celery_config)


def get_schedule(schedule):
    task_name = schedule[CELERYBEAT_SCHEDULE_TASK]
    sch = schedule[CELERYBEAT_SCHEDULE_SCH]
    beat_schedule = {}
    if sch == CRON:
        hour = schedule[CELERYBEAT_SCHEDULE_HOUR]
        minute = schedule[CELERYBEAT_SCHEDULE_MIN]
        beat_schedule[CELERYBEAT_SCHEDULE_TASK] = task_name
        beat_schedule[CELERYBEAT_SCHEDULE_SCH] = crontab(hour=hour, minute=minute)
    elif sch == TIMEDELTA:
        seconds = schedule[CELERYBEAT_SCHEDULE_SEC]
        beat_schedule[CELERYBEAT_SCHEDULE_TASK] = task_name
        beat_schedule[CELERYBEAT_SCHEDULE_SCH] = timedelta(seconds=seconds)
    else:
        # not adding support for anything apart from cron/timedelta based scheduling for now
        pass
    return beat_schedule


def create_queue(queue):
    name = queue[CELERY_QUEUE_NAME]
    exchange_type = queue[CELERY_QUEUE_EXCHANGE]
    routing_key = queue[CELERY_QUEUE_ROUTING_KEY]
    durable = queue[CELERY_QUEUES_DURABLE] if CELERY_QUEUES_DURABLE in queue else True
    if exchange_type == 'fanout':
        return Broadcast(name, exchnage=Exchange(type=exchange_type, routing_key=routing_key),
                         durable=durable, routing_key=routing_key, auto_delete=True)
    else:
        return Queue(name, exchange=Exchange(type=exchange_type),
                     durable=durable, routing_key=routing_key)


def configure_celeryd(name, prefix='celery'):
    celery = Celery(name)
    # Read environment variable that is set in prod mode that stores path of smarter.ini
    prod_config = get_config_file()
    conf = {}
    if prod_config:
        # This is the entry point for celeryd daemon
        print("Reading config for production mode")
        # Read from ini then pass the object here
        config = configparser.RawConfigParser()
        config.read(prod_config)
        section_name = 'app:main'
        options = config.options(section_name)
        for option in options:
            conf[option] = config.get(section_name, option)
        if 'environment.path' in conf:
            os.environ['PATH'] += os.pathsep + conf['environment.path']
        setup_celery(celery, conf, prefix=prefix)
    return (celery, conf)


def get_config_file():
    # Read environment variable that is set in prod mode that stores path of smarter.ini
    prod_config = os.environ.get("CELERY_PROD_CONFIG")
    file_name = prod_config if (prod_config is not None and os.path.exists(prod_config)) else None
    return file_name
