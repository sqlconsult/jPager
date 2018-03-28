#!/usr/bin/env python3

import csv
import pymongo


def txt_to_json(inp_file_path):
    # json_data = {}
    # json.dump(json_data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    # connect to mongodb on digital ocean droplet
    client = pymongo.MongoClient('mongodb://test_admin:admin@159.203.74.232:27017/test')
    # client.database_names()

    # reference jPager database name
    db = client['jPager']

    # delete any collections in jPager
    result = db['jPager'].delete_many({})
    del_count = result.deleted_count
    print('{0} rows deleted'.format(del_count))

    with open(inp_file_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print(80*'=')
        print(rows)
        print(80*'=')
        db['jPager'].insert_many(rows)

        # row_num = 1
        # for row in rows:
        #     # print(row_num, row)
        #     row_num += 1


# def read_file(inp_file_path):
#     with open(inp_file_path, 'r') as f:
#         csv_reader = csv.reader(f, delimiter='|')
#         header = csv_reader.__next__()
#
#         dept_name_idx = header.index('dept_name')
#         job_name_idx = header.index('job_name')
#         job_priority_idx = header.index('job_priority')
#         priority_name_idx = header.index('priority_name')
#         sla_time_idx  = header.index('sla_time')
#         user_name_idx = header.index('user_name')
#         user_email_idx = header.index('user_email')
#         user_phone_idx  = header.index('user_phone')
#         admin_idx = header.index('admin')
#         password_idx = header.index('password')
#         response_order_idx = header.index('response_order')
#
#         dept = {}
#         prev_dept_name = ''
#         prev_job_name = ''
#
#         for row in csv_reader:
#             dept_name = row[dept_name_idx]
#
#             dept_name = row[dept_name_idx]
#             job_name = row[job_name_idx]
#             job_priority = row[job_priority_idx]
#             priority_name = row[priority_name_idx]
#             sla_time = row[sla_time_idx]
#             user_name = row[user_name_idx]
#             user_email = row[user_email_idx]
#             user_phone = row[user_phone_idx]
#             admin = row[admin_idx]
#             password = row[password_idx]
#             response_order = row[response_order_idx]
#
#             print(row)


if __name__ == '__main__':
    file_nm = '../doc/SampleData.csv'
    txt_to_json(file_nm)
