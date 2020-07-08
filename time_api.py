"""This module connect aTimeLogger API."""
import requests
import json
import arrow
from datetime import datetime
from requests.auth import HTTPBasicAuth

INTERVAL_MAX = 100000
DAYS_NEW = 5


def get_auth_header():
    """
    Generate basic auth header for aTimeLogger.
    See the post for more info about the API, http://blog.timetrack.io/rest-api/
    """

    # get username and password from text file
    lines = [line.rstrip('\n') for line in open('pass.txt')]
    username, password, dev_token = lines
    return HTTPBasicAuth(username, password)


def get_types(auth_header):
    """
    Retrieve types data from aTimeLogger.
    :param auth_header: auth header for request data.
    :return: A list of dict for types data.
    """
    r_type = requests.get("https://app.atimelogger.com/api/v2/types",
                          auth=auth_header)
    types = json.loads(r_type.text)
    return types['types']


def get_all_intervals(auth_header):
    """
    Retrieve all intervals data from aTimeLogger. Number of entries is limited by INTERVAL_MAX.
    :param auth_header: auth header for request data.
    :return: A list of dict for intervals data.
    """
    r_interval = requests.get("https://app.atimelogger.com/api/v2/intervals",
                              params={'limit': INTERVAL_MAX, 'order': 'asc'},
                              auth=auth_header)
    intervals = json.loads(r_interval.text)
    return intervals['intervals']


def get_new_intervals(auth_header):
    """
    Retrieve new intervals data from aTimeLogger. New intervals is defined by DAYS_NEW.
    :param auth_header: auth header for request data.
    :return: A list of dict for intervals data.
    """
    now = arrow.get(datetime.now(), 'Asia/Shanghai')
    start = now.shift(days=-1).floor('day')
    r_interval = requests.get("https://app.atimelogger.com/api/v2/intervals",
                              params={'from': str(start.timestamp), 'to': str(now.timestamp)},
                              auth=auth_header)
    intervals = json.loads(r_interval.text)
    return intervals['intervals']

def main():
    auth_header = get_auth_header()
    types = get_types(auth_header)
    type_dict = {}
    for type in types:
        type_dict[type['guid']] = type['name']
    intervals = get_new_intervals(auth_header)
    daily_report = []
    for interval in intervals:
        t_from = datetime.fromtimestamp(interval['from']).strftime('%H:%M')
        t_to = datetime.fromtimestamp(interval['to']).strftime('%H:%M')
        hours, remainder = divmod(interval['to']-interval['from'], 60*60)
        minutes, seconds = divmod(remainder, 60)
        if hours == 0:
            t_length = '{}m'.format(minutes)
        else:
            t_length = '{}h{}m'.format(hours, minutes)
        t_type = type_dict[interval['type']['guid']]
        daily_report_item = '{} {} {} {}'.format(t_from, t_to, t_type, t_length)
        daily_report.append(daily_report_item)
    t_date = datetime.fromtimestamp(interval['to']).strftime('%Y-%m-%d')
    print (t_date)
    for i in daily_report[::-1]:
        print (i)

if __name__ == '__main__':
    main()