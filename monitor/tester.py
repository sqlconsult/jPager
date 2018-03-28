#!/usr/bin/env python3
import csv
from dateutil.parser import parse
import json
import pymongo


def read_params():
    with open('./params.json', 'r') as handle:
        json_params = json.load(handle)
    return json_params


def open_connection(params):
    # connect to MongoDb
    conn_str = 'mongodb://{user_name}:{password}@{ip_address}:{port}/{db_name}'.\
        format(user_name=params[0]['Mongo']['user_name'],
               password=params[0]['Mongo']['password'],
               ip_address=params[0]['Mongo']['ip_address'],
               port=params[0]['Mongo']['port'],
               db_name=params[0]['Mongo']['db_name'])
    # client = pymongo.MongoClient('mongodb://test_admin:admin@159.203.74.232:27017/test')
    client = pymongo.MongoClient(conn_str)
    return client


def get_xcns(params):
    client = open_connection(params)
    # client.database_names()

    db = client['jPager_xcn']     # test
    # db.collection_names()
    # ['sales', 'restaurants']

    cursor = db['jPager_xcn'].find({})
    for document in cursor:
        # print(document)
        # print(type(document))
        for key in document.keys():
            print('{0}: {1}'.format(key, document[key]))

    return True


def get_ref_data(params):
    client = open_connection(params)
    # client.database_names()

    db = client['jPager']     # test
    # db.collection_names()
    # ['sales', 'restaurants']

    cursor = db['jPager'].find({})
    for document in cursor:
        # print(document)
        # print(type(document))
        for key in document.keys():
            print('{0}: {1}'.format(key, document[key]))

    return True


def read_xcn_csv():
    with open('../setup/Alerts.csv') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        new_list = []
        # type integers and date times
        for row in rows:

            new_dict = {
                'alert_id': int(row['alert_id']),
                'dept_name': row['dept_name'],
                'job_name': row['job_name'],
                'user_name': row['user_name'],
                'user_email': row['user_email'],
                'sla_time': int(row['sla_time']),
                'response_order': int(row['response_order'])}

            if len(row['notification_dt']) > 0:
                new_dict['notification_dt'] = parse(row['notification_dt'])

            if len(row['response_dt']) > 0:
                new_dict['response_dt'] = parse(row['response_dt'])

            new_list.append(new_dict)

        print(type(new_list[0]))
        print(new_list)

    return True


def main():
    # params = read_params()
    #
    # ret_sts = get_xcns(params)
    # print(ret_sts)
    #
    # ret_sts = get_ref_data(params)
    # print(ret_sts)
    #
    # ret_sts = read_xcn_csv()
    # print(ret_sts)

    import datetime
    import time as t1
    utc_dt = datetime.datetime(2018, 3, 27, 15, 3, 37)
    ts = t1.time()
    utc_min_offset = -1 * (datetime.datetime.fromtimestamp(ts) - datetime.datetime.utcfromtimestamp(ts)).total_seconds()
    utc_hrs_offset = (utc_min_offset / 3600) + .5
    local_dt = utc_dt - datetime.timedelta(hours=utc_hrs_offset)

    print('utc_dt:', utc_dt)
    print('utc_min_offset:', utc_min_offset)
    print('utc_hrs_offset:', utc_hrs_offset)
    print('local_dt:', local_dt)


if __name__ == '__main__':
    main()
