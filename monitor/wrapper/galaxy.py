#!/usr/bin/env python3

# import datetime
import email
import imaplib
import smtplib

import datetime
import logging

class MailClass:
    def __init__(self, mail_server, user_name, user_pwd, module_logger):
        self.user_name = user_name
        self.user_pwd = user_pwd
        self.module_logger = module_logger
        self.imap_server = "mail.galaxy.net"
        self.imap_port = 993
        self.smtp_server = "mail.galaxy.net"
        self.smtp_port = 587
        # try up to 5 times to initialize object because imaplib.IMAP4_SSL might
        # encounter issues (for example, socket.gaierror: [Errno -3] Temporary
        # failure in name resolution
        num_try = 1
        max_try = 5
        success = False
        while not success and num_try < max_try:
            success = self.init_mail(mail_server)
            result = 'Successful' if success else 'Failed'
            msg = 'MailClass.init: Login attempt {0} of {1} - {2}'.format(num_try, max_try, result)
            module_logger.info(msg)
            num_try += 1

    def init_mail(self, mail_server):
        # self.mail = imaplib.IMAP4_SSL('mail.galaxy.net')
        try:
            self.mail_svr = imaplib.IMAP4_SSL(mail_server)
            return True
        except:
            return False

    def get_email(self, msg_id):
        self.mail_svr.select("inbox")  # connect to inbox.
        # For a given message id retrieve the raw mail message
        # print('msg_id:', msg_id)
        typ, data = self.mail_svr.fetch(msg_id, "(RFC822)")

        # raw_email = data[0][1].decode('UTF-8', 'replace')
        #
        # # print('get_email: raw_email:', raw_email)
        # self.raw_email = raw_email
        # self.email_message = email.message_from_string(self.raw_email)

        # print(data)

        msg = ''
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = self.mail_svr.message_from_string(response_part[1])

        return msg

    def get_emails_after_date(self, inp_date):
        # Get all emails after input date and return list of dictionary's
        # inp_date = datetime.datetime(2018, 4, 5)
        qry_date = inp_date.strftime("%d-%b-%Y")
        # print('qry_date:', qry_date)

        search_criteria = '(SINCE "{qry_date}")'.format(qry_date=qry_date)
        # print('search_criteria:', search_criteria)

        result, data = self.mail_svr.search(None, search_criteria, 'ALL')
        # print('typ:', typ)
        # print('data:', data)
        search_result = data[0].decode('UTF-8')
        # print('search_result:', 'xxx' + search_result + 'xxx')
        # if no messages (search_result has message ids) since input date return empty list
        stack = []
        if len(search_criteria) > 0:
            str_ids = search_result.split(' ')
            msg_ids = [int(x) for x in str_ids]

            for msg_id in msg_ids:
                raw_email = self.get_email(msg_id)
                parsed_email = self.parse_raw_email(msg_id, raw_email)
                stack.append(parsed_email)

        return stack

    def get_id_list(self):
        self.mail_svr.select("inbox")       # connect to inbox
        result, data = self.mail_svr.search(None, "ALL")
        print('result:', result)
        print('data:', data)
        ids = data[0].decode('UTF-8')   # data is a list.
        id_list = ids.split()           # ids is a space separated string
        print('id_list:', id_list)
        return id_list

    def get_latest_email(self):
        # get the latest message and return a dictionary
        msg_id_list = self.get_id_list()
        print('msg_id_list:', msg_id_list)
        latest_email_id = msg_id_list[-1]

        # fetch the email body (RFC822) for the given ID
        # result, data = self.mail_svr.fetch(latest_email_id, "(RFC822)")
        # raw_email = data[0][1].decode('UTF-8')

        raw_email = self.get_email(latest_email_id)
        parsed_email = self.parse_raw_email(latest_email_id, raw_email)

        return parsed_email

    def get_mbx_list(self):
        # Out: list of "folders" aka labels in gmail.
        mail_list = self.mail_svr.list()
        return mail_list

    def get_uid_list(self):
        self.mail_svr.select("inbox")  # connect to inbox.
        result, data = self.mail_svr.uid('search', None, "ALL")  # search and return uids instead
        ids = data[0].decode('UTF-8')  # data is a list.
        uid_list = ids.split()  # ids is a space separated string
        return uid_list

    def login(self):
        # self.mail_svr.login('byte_ic@galaxy-usa.com', 'rQ64sb#8')
        self.mail_svr.login(self.user_name, self.user_pwd)
        return True

    def logout(self):
        self.mail_svr.logout()

    def mail_body(self, raw_email):
        if raw_email.is_multipart():
            for payload in raw_email.get_payload():
                # if payload.is_multipart(): ...
                body = (
                    payload.get_payload()
                    .split(raw_email['from'])[0]
                    .split('\r\n\r\n2015')[0]
                )
                return body
        else:
            body = (
                raw_email.get_payload()
                .split(raw_email['from'])[0]
                .split('\r\n\r\n2015')[0]
            )
            return body

    def parse_raw_email(self, msg_id, raw_email):
        msg = {
            'msg_id': msg_id,
            'msg_body': self.mail_svr_body(raw_email),
            'msg_date': raw_email['Date'],
            'msg_from': raw_email['from'],
            'msg_reply_to': raw_email['Reply-To'],
            'msg_return_path': raw_email['Return-Path'],
            'msg_subject': raw_email['Subject'],
            'msg_to': raw_email['to']
        }
        return msg

    def send_email(self, recipient, subject, message):
        headers = "\r\n".join([
            "from: " + self.user_name,
            "subject: " + subject,
            "to: " + recipient,
            "mime-version: 1.0",
            "content-type: text/html"
        ])
        content = headers + "\r\n\r\n" + message
        while True:
            try:
                smtp_obj = smtplib.SMTP(self.smtp_server, self.smtp_port)
                smtp_obj.ehlo()
                smtp_obj.starttls()
                smtp_obj.login(self.user_name, self.user_pwd)
                smtp_obj.sendmail(self.user_name, recipient, content)
                self.module_logger.info('outlook.send_email: Message sent to {0}'.format(recipient))
                return True
            except:
                self.module_logger.error('outlook.send_email: Failed sending message {0}'.format(recipient))
                return False

def main():

    # Start logger
    app_name = __file__.split('.')[0]
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)
    start_logger(logger)
    module_logger = logging.getLogger('{app_name}.main'.format(app_name=app_name))

    email_id = 'byte_ic@galaxy-usa.com'
    email_pwd = 'rQ64sb#8'
    mail_x = MailClass('mail.galaxy.net', email_id, email_pwd, module_logger)
    mail_x.login()

    # for i in range(1009, 1012):
    #     send_test_message(mail, i)

    # get the latest
    tmp_list = mail_x.get_id_list()
    print(tmp_list)
    mail_x.logout()


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
