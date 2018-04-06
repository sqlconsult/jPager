#!/usr/bin/env python3

import datetime
import logging
import time as t1

# import smtplib
import outlook as outlook

# import re


# https://tools.ietf.org/html/rfc3501#section-6.4.45


def check_credentials(email_id, email_pwd, module_logger):
    # To check Credentials
    mail = outlook.Outlook(module_logger)
    ret_val = mail.login(email_id, email_pwd)
    return ret_val


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


def main():
    # Start logger
    app_name = __file__.split('.')[0]
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)
    start_logger(logger)

    module_logger = logging.getLogger('{app_name}.main'.format(app_name=app_name))
    module_logger.info('===== Starting =====')

    email_id = 'byte_maint@outlook.com'
    email_pwd = 'Byte1234'
    ans = check_credentials(email_id, email_pwd, module_logger)
    if ans:
        for i in range(1000, 1006):
            send_test_message(i, email_id, email_pwd, module_logger)

        # unread_msg = read_latest_unread_inbox()
        # if len(unread_msg) > 0:
        #     print(unread_msg)
        # else:
        #     print('No unread messages')

        # test_dt = datetime.date(2018, 3, 27)
        # msgs = read_after_date(test_dt, email_id, email_pwd)
        # for m1 in msgs:
        #     # only look at messages with the word 'failed' in the subject line
        #     if 'failed' in m1.mail_subject.lower():
        #         # must also have Job # (up to 10 digits)
        #         # regex = '^Test Job d{0,10}.*$'
        #
        #         # if re.match(regex, m1.mail_subject):
        #         if True:
        #             # convert message date/time to UTC
        #             msg_dt = convert_to_date(m1.mail_datetime)
        #             print(50*'=')
        #             print(' Subject:', m1.mail_subject)
        #
        #             print('    From:', m1.mail_from)
        #             print('      To:', m1.mail_to)
        #             print('    Date:', m1.mail_datetime)
        #             print('Lcl Date:', msg_dt)
        #             print(80 * '=')
        #             print('message body:', type(m1.mail_body))
        #             print(m1.mail_body)
        #             print(80*'=')

    else:
        print('Credential check failed!')
    module_logger.info('===== Done =====')


def read_after_date(msg_rcv_dt, email_id, email_pwd, module_logger):
    # Read messages after specified date
    mail = outlook.Outlook(module_logger)
    mail.login(email_id, email_pwd)
    mail.inbox()
    return mail.unread_after_date(msg_rcv_dt)


def read_latest_unread_inbox(email_id, email_pwd, module_logger):
    # get latest Unread Message in inbox :
    mail = outlook.Outlook(module_logger)
    mail.login(email_id, email_pwd)
    mail.inbox()
    return mail.unread()


def read_latest_unread_junk(email_id, email_pwd, module_logger):
    # To get latest Unread Message in Junk :
    mail = outlook.Outlook(module_logger)
    mail.login(email_id, email_pwd)
    mail.junk()
    return mail.unread()


# def send_mail(email_id, email_pwd):
#     conn = smtplib.SMTP('smtp-mail.outlook.com', 587)
#     # print(type(conn))
#     conn.ehlo()
#     conn.starttls()
#     conn.login(email_id, email_pwd)
#
#     msg_from = 'byte_maint@outlook.com'
#     msg_cc = 'bbyte_ic@outlook.com'
#     msg_subject = 'Subject:Test Subject\n\n' \
#                   + 'We the People of the United States, in Order to form a more perfect Union, ' \
#                   + 'establish Justice, insure domestic Tranquility, provide for the common ' \
#                   + 'defence,[note 1] promote the general Welfare, and secure the Blessings of ' \
#                   + 'Liberty to ourselves and our Posterity, do ordain and establish this ' \
#                   + 'Constitution for the United States of America.'
#     conn.sendmail(msg_from, msg_cc, msg_subject)
#     conn.quit()


def send_test_message(job_num, email_id, email_pwd, module_logger):
    # To send Message :

    msg_recipient = 'byte_ic@outlook.com'
    msg_subject = 'Job {job_num} - Job Name {job_num} - Failed'.format(job_num=job_num)
    body_hdr = '{0}\n\n{1}\n\n'.format(msg_subject, 80*'=')
    msg_body = body_hdr\
               + 'We the People of the United States, in Order to form a more perfect Union, ' \
               + 'establish Justice, insure domestic Tranquility, provide for the common ' \
               + 'defence,[note 1] promote the general Welfare, and secure the Blessings of ' \
               + 'Liberty to ourselves and our Posterity, do ordain and establish this ' \
               + 'Constitution for the United States of America.'

    mail = outlook.Outlook(module_logger)
    mail.login(email_id, email_pwd)
    mail.send_email(msg_recipient, msg_subject, msg_body)


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


if __name__ == '__main__':
    main()
