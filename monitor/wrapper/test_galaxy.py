#!/usr/bin/env python3

import datetime
import json
import logging
import pprint
import time as t1

import galaxy


def main():
    # Instantiate json pretty printer
    pp = pprint.PrettyPrinter(indent=4)

    # Start logger
    app_name = __file__.split('.')[0]
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)
    start_logger(logger)

    module_logger = logging.getLogger('{app_name}.main'.format(app_name=app_name))
    module_logger.info('===== Starting =====')

    module_logger.info('Read json parameters')
    with open('../params.json', 'r') as handle:
        json_params = json.load(handle)

    email_id = json_params[0]['MailBoxToMonitor']
    email_pwd = json_params[0]['MailBoxPassword']

    mail_x = galaxy.MailClass('mail.galaxy.net', email_id, email_pwd, module_logger)
    mail_x.login()

    # for i in range(1009, 1012):
    #     send_test_message(mail, i)

    # get the latest
    tmp_list = mail_x.get_id_list()
    print(tmp_list)

    # latest_email = mail.get_latest_email()
    # module_logger.info(latest_email)

    module_logger.info('===== Done =====')


def convert_to_date(inp_dt):
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    date_parts = inp_dt.split()
    day_num = date_parts[1]
    month_str = date_parts[2].lower()
    month = months.index(month_str) + 1

    year = date_parts[3]
    time = date_parts[4]
    offset = float(date_parts[5][1::]) * 0.01
    sign = date_parts[5][0]

    utc_offset = offset if sign == '+' else -1 * offset

    # time_str = '{year}-{month}-{day_num}T{time}{sign}{offset}'.\
    #    format(year=year, month=month, day_num=day_num, time=time, sign=sign, offset=offset )

    time_str = '{year}-{month}-{day_num}T{time}'. \
        format(year=year, month=month, day_num=day_num, time=time)

    # print('time_str:', time_str, 'utc_offset:', utc_offset)

    base_dt = datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')

    # print('base_dt:', base_dt)

    utc_dt = base_dt + datetime.timedelta(hours=utc_offset)

    # convert utc datetime to local datetime
    ts = t1.time()
    utc_min_offset = -1 * (datetime.datetime.fromtimestamp(ts) - datetime.datetime.utcfromtimestamp(ts)).total_seconds()
    utc_hrs_offset = utc_min_offset / 3600
    local_dt = utc_dt - datetime.timedelta(hours=utc_hrs_offset)

    return local_dt


def start_logger(p_logger):
    # Create file handler which logs debug messages
    log_fil_nm = 'log_{date:%Y%m%d_%H%M%S}.log'.format(date=datetime.datetime.now())
    fh = logging.FileHandler(log_fil_nm)
    fh.setLevel(logging.DEBUG)

    # Create console handler with a higher log level, error
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    p_logger.addHandler(fh)
    p_logger.addHandler(ch)


def send_test_message(mail_obj, job_num):
    # To send Message :

    msg_recipient = 'byte_ic@galaxy-usa.com'
    msg_subject = 'Job {job_num} - Job Name {job_num} - Failed'.format(job_num=job_num)
    body_hdr = '{0}\n\n{1}\n\n'.format(msg_subject, 80*'=')
    msg_body = body_hdr\
               + 'We the People of the United States, in Order to form a more perfect Union, ' \
               + 'establish Justice, insure domestic Tranquility, provide for the common ' \
               + 'defence,[note 1] promote the general Welfare, and secure the Blessings of ' \
               + 'Liberty to ourselves and our Posterity, do ordain and establish this ' \
               + 'Constitution for the United States of America.'

    mail_obj.send_email(msg_recipient, msg_subject, msg_body)


if __name__ == '__main__':
    main()