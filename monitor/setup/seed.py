#!/usr/bin/env python3

import csv
import datetime
import json
from dateutil.parser import parse
import pymongo


def delete_all(db, db_name):
    # delete all collections in db_name database
    result = db[db_name].delete_many({})
    del_count = result.deleted_count
    print('Seed: {0} rows deleted from {1}'.format(del_count, db_name))

    return db


def import_ref_data(inp_file_path, client):
    # clear jPager reference database
    db_name = 'jPager'
    db = client[db_name]
    delete_all(db, db_name)

    # populate jPager reference database
    with open(inp_file_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        # print(80*'=')
        # print(rows)
        # print(80*'=')
        db['jPager'].insert_many(rows)

    return True


def init_transactions(inp_file_path, client):
    # clear jPager transaction database
    db_name = 'jPager_xcn'
    db = client[db_name]
    delete_all(db, db_name)

    # genesis entry
    seed_list = [{
        "dept_name": "jedi",
        "job_name": "may_the_force_be with_you",
        "user_name": "n_kata_del_gormo",
        "user_email": "",
        "sla_time": 999,
        "response_order": 1,
        "notification_dt": datetime.datetime(2018, 1, 1, 0, 0, 1),
        "response_dt": datetime.datetime(2018, 1, 1, 23, 59, 59)
    }]

    # seed jPager xcn database with some test data
    with open(inp_file_path) as f:
        # read csv test data into a dictionary
        reader = csv.DictReader(f)
        rows = list(reader)

        # convert input strings to integers and date times
        for row in rows:
            new_dict = {
                'dept_name': row['dept_name'],
                'job_name': row['job_name'],
                'email_from': row['email_from'],
                'user_name': row['user_name'],
                'email_to': row['email_to'],
                'sla_time': int(row['sla_time']),
                'response_order': int(row['response_order'])}

            if len(row['notification_dt']) > 0:
                new_dict['notification_dt'] = parse(row['notification_dt'])

            if len(row['response_dt']) > 0:
                new_dict['response_dt'] = parse(row['response_dt'])

            seed_list.append(new_dict)

    db[db_name].insert_many(seed_list)

    return True


def main():
    seed_data_paths = ['RefData.csv', 'Alerts.csv']
    seed_tables(seed_data_paths)


def open_connection(params):
    # connect to MongoDb
    conn_str = 'mongodb://{user_name}:{password}@{ip_address}:{port}/{db_name}'.\
        format(user_name=params[0]['Mongo']['user_name'],
               password=params[0]['Mongo']['password'],
               ip_address=params[0]['Mongo']['ip_address'],
               port=params[0]['Mongo']['port'],
               db_name=params[0]['Mongo']['db_name'])
    print('Connection string:', conn_str)
    # client = pymongo.MongoClient('mongodb://test_admin:admin@159.203.74.232:27017/test')
    client = pymongo.MongoClient(conn_str)
    return client


def seed_tables(seed_data_paths):
    # json_data = {}
    # json.dump(json_data, outfile, sort_keys=True, indent=4, ensure_ascii=False)
    print('Read json parameters')
    with open('../params.json', 'r') as handle:
        json_params = json.load(handle)

    # connect to mongodb on digital ocean droplet
    print('Open connection')
    client = open_connection(json_params)
    # client.database_names()

    print('Import reference data')
    import_ref_data(seed_data_paths[0], client)

    print('Seed initial transaction')
    init_transactions(seed_data_paths[1], client)

    client.close()
    return True


if __name__ == '__main__':
    print('Start')
    main()
    print('Done')
