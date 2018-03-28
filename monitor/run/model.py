#!/usr/bin/env python3

import datetime
import pymongo


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


def get_existing_alerts(params):
    #
    # sample mongo cli commands
    #
    # db['jPager'].find({ "job_name":"Test Job 1001" }).pretty()
    # db['jPager'].find({"job_name": "Test Job 1001"}).limit(2).sort({"response_order": 1}).pretty()
    #
    # sample mongodb commands
    #
    # client.database_names()
    # db.collection_names()
    # ['sales', 'restaurants']

    # open database connection
    client = open_connection(params)

    # point to jPager alerts
    db = client['jPager_xcn']

    # get all open alerts
    docs = db['jPager_xcn'].find({})

    # display for debugging purpose
    # print(80*'=')
    # import pprint
    # pp = pprint.PrettyPrinter(indent=4)
    # for doc in docs:
    #     pp.pprint(doc)
    # print(80*'=')

    """
    Sample document
    ====== ========
    'alert_id': 5,
    'dept_name': 'IT',
    'email_from': 'byte_ic@outlook.com',
    'email_to': 'byte_maint@outlook.com',
    'job_name': 'Test Job 1001',
    'notification_dt': datetime.datetime(2018, 3, 26, 10, 20, 23),
    'response_dt': datetime.datetime(2018, 3, 26, 10, 45, 23),   <<<<<<<< CLOSE >>>>>>
    'response_order': 1,
    'sla_time': 75,
    'user_name': 'IndividualContributor'
    """

    # leave only alerts that have not been replied to
    docs.rewind()
    result_dict = {}
    row_num = 1
    for doc in docs:
        # skip initial document
        if doc['dept_name'] == 'jedi':
            continue

        # format alert open date time YYYYMMDD_HHMMSS
        # print(doc['job_name'], doc['email_from'], doc['response_order'], doc['notification_dt'])
        str_dt = datetime.datetime.strftime(doc['notification_dt'], '%Y%m%d_%H%M%S')
        key = '{0}~{1}~{2}~{3}'.\
            format(doc['job_name'], doc['email_from'], doc['response_order'], str_dt)

        print('key {0}: {1}'.format(row_num, key))

        # if there is a response_dt key in the document, this is an alert reply (close)
        if 'response_dt' in doc:
            print('   {0} close'.format(row_num))
            # closing event should have last response order
            # delete any open's for this close from in-memory cache
            last_response_order = doc['response_order']
            for i in range(1, last_response_order+1):
                tmp_key = '{0}~{1}~{2}~{3}'.\
                    format(doc['job_name'], doc['email_to'], i, str_dt)
                if tmp_key in result_dict:
                    print('    {0} tmp_key: {1}'.format(row_num, tmp_key))
                    del result_dict[tmp_key]
        else:
            # this is an alert (open)
            # add it to in-memory cache
            new_alert = {
                '_id': doc['_id'],
                'dept_name': doc['job_name'],
                'job_name': doc['job_name'],
                'email_from': doc['email_from'],
                'user_name': doc['user_name'],
                'email_to': doc['email_to'],
                'sla_time':  doc['sla_time'],
                'response_order': doc['response_order']
            }
            result_dict[key] = new_alert

        row_num += 1

    # close connection
    client.close()

    return result_dict
