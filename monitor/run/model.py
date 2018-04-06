#!/usr/bin/env python3

import datetime
from dateutil.parser import parse
import pymongo
import wrapper.outlook as outlook


def escalate_job_alerts(alerts, ref_data, params, module_logger):
    #
    # alerts key   = job_name~email_from~response_order~YYYYMMDD_HHMMSS
    # ref data key = dept_name~job_name~response_order
    #
    cur_dt = datetime.datetime.now()
    for key, alert in alerts.items():
        # print(type(alert), alert)
        notify_dt = alert['notification_dt']
        sla_minutes = alert['sla_time']
        escalate_dt = notify_dt + datetime.timedelta(minutes=sla_minutes)

        if escalate_dt < cur_dt:
            # this job alert needs to be escalated to next person
            # send mail to everyone from this 1 (original) to this resp_order+1
            resp_order = alert['response_order'] + 1

            for i in range(1, resp_order+1):
                ref_key = '{0}~{1}~{2}'.format(alert['dept_name'], alert['job_name'], i)

                if ref_key in ref_data:
                    # print(ref_data[ref_key])
                    recipient = ref_data[ref_key]['user_email']
                    send_mail(params, alert, recipient, i, module_logger)

    return True


def get_existing_open_alerts(alerts, module_logger):
    """
    Sample document
    ====== ========
       {
            "index": 2,
            "previous_hash": "46cd4ee66bd03062e79b7c6ee651651e3836c2e2a52e3421d8aebd1aa7ad48ff",
            "proof": 616,
            "timestamp": "2018-04-04 10:30:10",
            "transactions": [
                {
                    "dept_name": "IT",
                    "email_from": "byte_maint@outlook.com",
                    "email_subject": "Test Job 1000 Failed",
                    "email_to": "byte_ic@outlook.com",
                    "job_name": "Test Job 1000",
                    "job_failure_dt": "2018-01-01 00:00:01"
                    "notification_dt": "2018-03-26 10:00:23",
                    "response_dt": "2018-03-26 10:45:23",
                    "response_order": 1,
                    "sla_time": 15,
                    "user_name": "IndividualContributor"
                }
            ]
        },
    """
    result_dict = {}
    for a1 in alerts:

        # skip genesis block
        alert = a1['transactions'][0]
        if alert['dept_name'] == 'jedi':
            continue

        # format alert open date time YYYYMMDD_HHMMSS
        # print(alert['job_name'], alert['email_from'], alert['response_order'], alert['job_failure_dt'])
        tmp_dt = parse(alert['job_failure_dt'])
        str_dt = datetime.datetime.strftime(tmp_dt, '%Y%m%d_%H%M%S')
        key = '{0}~{1}~{2}'.\
            format(alert['job_name'], str_dt, int(alert['response_order']))

        # print('key {0}: {1}'.format(row_num, key))

        # response date only exists in alert closing event
        # and does NOT have to be kept in the return results
        # because only open events are returned
        # if 'response_dt' in alert_detail.keys():
        #     new_alert['response_dt'] = parse(alert_detail['response_dt'])

        # if there is a response_dt key in the alert, this is an alert reply (close)
        if 'response_dt' in alert:
            # print('   {0} close'.format(row_num))
            # closing event should have last response order
            # delete open for this close from in-memory cache
            tmp_key = '{0}~{1}~{2}'.\
                format(alert['job_name'], str_dt, int(alert['response_order']))
            # print('got closing alert for {0}'.format(tmp_key))
            if tmp_key in result_dict:
                # print('    {0} tmp_key: {1}'.format(row_num, tmp_key))
                del result_dict[tmp_key]
        else:
            # this is an alert (open)
            # keep only last open alert.  escalation handles sending alerts to
            # previous members and next person in list
            prev_resp_order = int(alert['response_order']) - 1

            if prev_resp_order < int(alert['response_order']):
                tmp_key = '{0}~{1}~{2}'.\
                    format(alert['job_name'], str_dt, prev_resp_order)
                # print('add new alert (key, tmp_key)', key, tmp_key)
                if tmp_key in result_dict:
                    # print('tmp_key in result_dict')
                    del result_dict[tmp_key]

            # add it to in-memory cache
            new_alert = {
                '_id': a1['index'],
                'dept_name': alert['dept_name'],
                'email_from': alert['email_from'],
                'email_subject': alert['email_subject'],
                'email_to': alert['email_to'],
                'job_name': alert['job_name'],
                'job_failure_dt': parse(alert['job_failure_dt']),
                'notification_dt': parse(alert['notification_dt']),
                'response_order': int(alert['response_order']),
                'sla_time': int(alert['sla_time']),
                'user_name': alert['user_name']
            }

            result_dict[key] = new_alert

    module_logger.info('model.get_existing_open_alerts: {0} of {1} alerts is still open'.
                       format(len(result_dict), len(alerts)))
    return result_dict


def get_existing_alerts(params):
    #######################################################
    #                                                     #
    #  NOT USED - KEPT AROUND FOR MONGO DEB EXAMPLE       #
    #                                                     #
    #######################################################
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
    alert_db = params[0]['Mongo']['alert_db_name']
    client = open_connection(params, alert_db)

    # point to jPager alerts
    db = client[alert_db]

    # get all open alerts
    docs = db[alert_db].find({})

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
       {
            "index": 2,
            "previous_hash": "46cd4ee66bd03062e79b7c6ee651651e3836c2e2a52e3421d8aebd1aa7ad48ff",
            "proof": 616,
            "timestamp": "2018-04-04 10:30:10",
            "transactions": [
                {
                    "dept_name": "IT",
                    "email_from": "byte_maint@outlook.com",
                    "email_subject": "Test Job 1000 Failed",
                    "email_to": "byte_ic@outlook.com",
                    "job_name": "Test Job 1000",
                    "notification_dt": "2018-03-26 10:00:23",
                    "response_order": 1,
                    "sla_time": 15,
                    "user_name": "IndividualContributor"
                }
            ]
        },
    """

    # leave only alerts that have not been replied to
    docs.rewind()
    result_dict = {}
    row_num = 1
    for doc in docs:
        # skip genesis block
        if doc['dept_name'] == 'jedi':
            continue

        # format alert open date time YYYYMMDD_HHMMSS
        # print(doc['job_name'], doc['email_from'], doc['response_order'], doc['notification_dt'])
        str_dt = datetime.datetime.strftime(doc['notification_dt'], '%Y%m%d_%H%M%S')
        key = '{0}~{1}~{2}~{3}'.\
            format(doc['job_name'], doc['email_from'], doc['response_order'], str_dt)

        # print('key {0}: {1}'.format(row_num, key))

        # if there is a response_dt key in the document, this is an alert reply (close)
        if 'response_dt' in doc:
            # print('   {0} close'.format(row_num))
            # closing event should have last response order
            # delete any open's for this close from in-memory cache
            last_response_order = doc['response_order']
            for i in range(1, last_response_order+1):
                tmp_key = '{0}~{1}~{2}~{3}'.\
                    format(doc['job_name'], doc['email_to'], i, str_dt)
                if tmp_key in result_dict:
                    # print('    {0} tmp_key: {1}'.format(row_num, tmp_key))
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


def get_ref_data(params):
    # open database connection
    ref_db = params[0]['Mongo']['ref_db_name']
    client = open_connection(params, ref_db)

    # point to reference database
    db = client[ref_db]

    # get all open alerts
    docs = db[ref_db].find({})

    # display for debugging purpose
    # print(80*'=')
    # import pprint
    # pp = pprint.PrettyPrinter(indent=4)
    # for doc in docs:
    #     pp.pprint(doc)
    # print(80*'=')

    """
        Sample Document
        ====== ========
        "_id" : ObjectId("5aba7e2ec405bc22af7355f0"),
        "priority_name" : "high",
        "response_order" : "2",
        "dept_name" : "IT",
        "user_email" : "byte_mgr@outlookcom",
        "job_name" : "Test Job 1000",
        "admin" : "TRUE",
        "user_phone" : "2125551212",
        "user_name" : "Manager",
        "password" : "mgr1234",
        "job_priority" : "1",
        "sla_time" : "15"
    """
    docs.rewind()
    return_dict = {}
    for doc in docs:
        key = '{0}~{1}~{2}'.format(doc["dept_name"], doc['job_name'], doc['response_order'])
        new_ref_data = {
            "priority_name": doc["priority_name"],
            "response_order": int(doc["response_order"]),
            "dept_name": doc["dept_name"],
            "user_email": doc["user_email"],
            "job_name": doc["job_name"],
            "admin": doc["admin"].lower() == "true",
            "user_phone": doc["user_phone"],
            "user_name": doc["user_name"],
            "password": doc["password"],
            "job_priority": int(doc["job_priority"]),
            "sla_time": int(doc["sla_time"])
        }
        return_dict[key] = new_ref_data

    return return_dict


def open_connection(params, db_name):
    # connect to MongoDb
    # print(db_name)
    conn_str = 'mongodb://{user_name}:{password}@{ip_address}:{port}/{db_name}'.\
        format(user_name=params[0]['Mongo']['user_name'],
               password=params[0]['Mongo']['password'],
               ip_address=params[0]['Mongo']['ip_address'],
               port=params[0]['Mongo']['port'],
               db_name=db_name)
    # print(conn_str)
    # client = pymongo.MongoClient('mongodb://test_admin:admin@159.203.74.232:27017/test')
    client = pymongo.MongoClient(conn_str)
    return client


def send_mail(params, alert, recipient, response_order, module_logger):
    msg_recipient = recipient
    msg_subject = alert['email_subject']

    failure_dt = '{dt:%Y-%m-%d %H:%M:%S}'.format(dt=alert['job_failure_dt'])

    msg_body = 'Job Name: {job_name}\n' \
               'Job Failure Datetime: {job_failure_dt}\n'\
               'Escalation Order: {response_order}\n' \
               'SLA Time (minutes): {sla_time}'.\
                   format(job_name=alert['job_name'],
                          job_failure_dt=failure_dt,
                          response_order=response_order,
                          sla_time=alert['sla_time'])

    # print('msg_recipient:', msg_recipient)
    # print('msg_subject:', msg_subject)
    # print('msg_body:', msg_body)
    # print(80*'=')
    log_msg = 'Sent email to {0} regarding {1}'.format(msg_recipient, msg_subject)
    module_logger.info(log_msg)
    # TODO: mail = outlook.Outlook()
    # TODO: mail.login(params[0]['MailBoxToMonitor'], params[0]['MailBoxPassword'])
    # TODO: mail.sendEmail(msg_recipient, msg_subject, msg_body)
