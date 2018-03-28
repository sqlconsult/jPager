import datetime
import smtplib
import outlook
import re

email_id = 'byte_student@outlook.com'
email_pwd = 'Byte1234'

# https://tools.ietf.org/html/rfc3501#section-6.4.4


def send_mail():
    conn = smtplib.SMTP('smtp-mail.outlook.com', 587)
    print(type(conn))
    conn.ehlo()
    conn.starttls()
    conn.login(email_id, email_pwd)

    msg_from = 'byte_student@outlook.com'
    msg_cc = 'byte_student@outlook.com'
    msg_subject = 'Subject:Test Subject\n\n' \
                  + 'We the People of the United States, in Order to form a more perfect Union, ' \
                  + 'establish Justice, insure domestic Tranquility, provide for the common ' \
                  + 'defence,[note 1] promote the general Welfare, and secure the Blessings of ' \
                  + 'Liberty to ourselves and our Posterity, do ordain and establish this ' \
                  + 'Constitution for the United States of America.'
    conn.sendmail(msg_from, msg_cc, msg_subject)
    conn.quit()


def read_latest_unread_inbox():
    # get latest Unread Message in inbox :
    mail = outlook.Outlook()
    mail.login(email_id, email_pwd)
    mail.inbox()
    return mail.unread()


def read_latest_unread_junk():
    # To get latest Unread Message in Junk :
    mail = outlook.Outlook()
    mail.login(email_id, email_pwd)
    mail.junk()
    return mail.unread()


def read_after_date(msg_rcv_dt):
    # To get latest Unread Message in Junk :
    mail = outlook.Outlook()
    mail.login(email_id, email_pwd)
    mail.inbox()
    return mail.unreadIdsAfter(msg_rcv_dt)


def send_test_message(job_num):
    # To send Message :

    msg_recipient = 'byte_student@outlook.com'
    msg_subject = 'Job {job_num} - Job Name {job_num} - Failed'.format(job_num=job_num)
    msg_body = 'We the People of the United States, in Order to form a more perfect Union, ' \
               + 'establish Justice, insure domestic Tranquility, provide for the common ' \
               + 'defence,[note 1] promote the general Welfare, and secure the Blessings of ' \
               + 'Liberty to ourselves and our Posterity, do ordain and establish this ' \
               + 'Constitution for the United States of America.'

    mail = outlook.Outlook()
    mail.login(email_id, email_pwd)
    mail.sendEmail(msg_recipient, msg_subject, msg_body)


def check_credentials():
    # To check Credentials:
    mail = outlook.Outlook()
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

    time_str = '{year}-{month}-{day_num}T{time}'.\
        format(year=year, month=month, day_num=day_num, time=time)

    # print('time_str:', time_str, 'utc_offset:', utc_offset)

    base_dt = datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')

    # print('base_dt:', base_dt)

    utc_dt = base_dt + datetime.timedelta(hours=utc_offset)

    return utc_dt


if __name__ == '__main__':
    ans = check_credentials()
    if ans:
        #for i in range(5):
        #    send_test_message(i)

        # unread_msg = read_latest_unread_inbox()
        # if len(unread_msg) > 0:
        #     print(unread_msg)
        # else:
        #     print('No unread messages')

        test_dt = datetime.date(2018, 3, 8)
        msgs = read_after_date(test_dt)
        for m1 in msgs:
            # only look at messages with the word 'failed' in the subject line
            if 'failed' in m1.mail_subject.lower():
                # must also have Job # (up to 10 digits)
                regex = '^Job d{0,10}.*$'

                if re.match(regex, m1.mail_subject):
                # if True:
                    msg_dt = convert_to_date(m1.mail_datetime)
                    print(50*'=')
                    print('Subject:', m1.mail_subject)

                    print('   From:', m1.mail_from)
                    print('     To:', m1.mail_to)
                    print('   Date:', m1.mail_datetime)
                    print('        ', msg_dt)

    else:
        print('Credential check failed!')