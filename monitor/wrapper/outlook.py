#!/usr/bin/env python3

import galaxy
import imaplib
import smtplib
import datetime
import galaxy.mime.multipart
import base64
import outlook_config as config

#########################################################################
#             From: https://github.com/awangga/outlook                  #
#                                                                       #
#    https://tools.ietf.org/html/rfc3501#section-6.4.4                  #
#                                                                       #
#########################################################################


class Outlook:

    def __init__(self, module_logger):
        # try up to 5 times to initialize object because imaplib.IMAP4_SSL might
        # encounter issues (for example, socket.gaierror: [Errno -3] Temporary
        # failure in name resolution
        #
        # imaplib.IMAP4_SSL: The connection is created and protocol version
        # (IMAP4 or IMAP4rev1) is determined when the instance is initialized
        num_try = 0
        max_try = 5
        success = False
        while not success and num_try < max_try:
            success = self.init_obj()
            if not success:
                print('Connection attempt {num_try} of {max_try}'.
                      format(num_try=num_try, max_try=max_try))
            num_try += 1
        self.logger = module_logger
        # self.imap = imaplib.IMAP4_SSL('imap-mail.outlook.com')
        # self.smtp = smtplib.SMTP('smtp-mail.outlook.com')

    def init_obj(self):
        try:
            mydate = datetime.datetime.now() - datetime.timedelta(1)
            self.today = mydate.strftime("%d-%b-%Y")
            self.username = ''
            self.password = ''
            self.imap = imaplib.IMAP4_SSL(config.imap_server, config.imap_port)
            self.raw_email = ''
            self.email_message = ''
            self.smtp = smtplib.SMTP(config.smtp_server, config.smtp_port)
            return True
        except:
            return False

    def all_ids(self):
        r, d = self.imap.search(None, "ALL")
        ret_val = d[0].split(' ')
        return ret_val

    def get_email(self, msg_id):
        print('msg_id:', msg_id)
        typ, data = self.imap.fetch(msg_id, "(RFC822)")

        # raw_email = data[0][1].decode('UTF-8', 'replace')
        #
        # # print('get_email: raw_email:', raw_email)
        # self.raw_email = raw_email
        # self.email_message = email.message_from_string(self.raw_email)

        print(data)

        for response_part in data:
            if isinstance(response_part, tuple):
                msg = galaxy.message_from_string(response_part[1])

        self.email_message = msg

        return self.email_message

    def get_ids_with_word(self, ids, word):
        stack = []
        for id1 in ids:
            self.get_email(id1)
            if word in self.mail_body().lower():
                stack.append(id1)
        return stack

    def get_mailboxes(self):
        typ, data = self.imap.list()
        return typ, data

    def get_uids(self):
        typ, data = self.imap.uid('search', None, "ALL")  # search and return uids instead
        # latest_email_uid = data[0].split()[-1]
        # result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
        # raw_email = data[0][1]
        return typ, data

    def has_unread(self):
        ret_val = self.unread_ids()
        return ret_val != []

    def inbox(self):
        return self.imap.select("INBOX")

    def junk(self):
        return self.imap.select("INBOX.Spam")

    def login(self, username, password):
        self.username = username
        self.password = password
        while True:
            try:
                self.imap = imaplib.IMAP4_SSL(config.imap_server, config.imap_port)
                r, d = self.imap.login(username, password)
                assert r == 'OK', 'login failed'
                self.logger.info('outlook.login: Login successful')
                return True
            except:
                self.logger.error('outlook.login: Login failed')
                return False

    def mail_all(self):
        return self.email_message

    def mail_body(self):
        if self.email_message.is_multipart():
            for payload in self.email_message.get_payload():
                # if payload.is_multipart(): ...
                body = (
                    payload.get_payload()
                    .split(self.email_message['from'])[0]
                    .split('\r\n\r\n2015')[0]
                )
                return body
        else:
            body = (
                self.email_message.get_payload()
                .split(self.email_message['from'])[0]
                .split('\r\n\r\n2015')[0]
            )
            return body

    def mail_body_decoded(self):
        return base64.urlsafe_b64decode(self.mail_body())

    def mail_date(self):
        return self.email_message['Date']

    def mail_from(self):
        return self.email_message['from']

    def mail_reply_to(self):
        return self.email_message['Reply-To']

    def mail_return_path(self):
        return self.email_message['Return-Path']

    def mail_subject(self):
        return self.email_message['Subject']

    def mail_to(self):
        return self.email_message['to']

    def logout(self):
        return self.imap.logout()

    def raw_read(self):
        ret_val = self.read_ids()
        latest_id = ret_val[-1]
        r, d = self.imap.fetch(latest_id, "(RFC822)")
        self.raw_email = d[0][1]
        return self.raw_email

    def read(self):
        ret_val = self.read_ids()
        latest_id = ret_val[-1]
        return self.get_email(latest_id)

    def read_ids(self):
        r, d = self.imap.search(None, "SEEN")
        ret_val = d[0].split(' ')
        return ret_val

    def read_ids_today(self):
        r, d = self.imap.search(None, '(SINCE "'+self.today+'")', 'SEEN')
        ret_val = d[0].split(' ')
        return ret_val

    def read_only(self, folder):
        return self.imap.select(folder, readonly=True)

    def read_today(self):
        ret_val = self.read_ids_today()
        latest_id = ret_val[-1]
        return self.get_email(latest_id)

    def select(self, inp_str):
        return self.imap.select(inp_str)

    def send_email(self, recipient, subject, message):
        headers = "\r\n".join([
            "from: " + self.username,
            "subject: " + subject,
            "to: " + recipient,
            "mime-version: 1.0",
            "content-type: text/html"
        ])
        content = headers + "\r\n\r\n" + message
        while True:
            try:
                self.smtp = smtplib.SMTP(config.smtp_server, config.smtp_port)
                self.smtp.ehlo()
                self.smtp.starttls()
                self.smtp.login(self.username, self.password)
                self.smtp.sendmail(self.username, recipient, content)
                self.logger.info('outlook.send_email: Message sent to {0}'.format(recipient))
                return True
            except:
                self.logger.error('outlook.send_email: Failed sending message {0}'.format(recipient))
                return False

    def send_email_mime(self, recipient, subject, message):
        msg = galaxy.mime.multipart.MIMEMultipart()
        msg['to'] = recipient
        msg['from'] = self.username
        msg['subject'] = subject
        msg.add_header('reply-to', self.username)
        # headers = "\r\n".join(["from: " + "sms@kitaklik.com","subject: " +
        #     subject,"to: " + recipient,"mime-version: 1.0","content-type: text/html"])
        # content = headers + "\r\n\r\n" + message
        try:
            self.smtp = smtplib.SMTP(config.smtp_server, config.smtp_port)
            self.smtp.ehlo()
            self.smtp.starttls()
            self.smtp.login(self.username, self.password)
            self.smtp.sendmail(msg['from'], [msg['to']], msg.as_string())
            self.logger.info('outlook.send_email_mime: Message sent to {0}'.format(recipient))
            return True
        except smtplib.SMTPException:
            self.logger.error('outlook.send_email_mime: Failed sending message {0}'.format(recipient))
            return False

    @staticmethod
    def today(self):
        tmp_date = datetime.datetime.now()
        return tmp_date.strftime("%d-%b-%Y")

    def unread(self):
        ret_val = self.unread_ids()
        if ret_val:
            latest_id = ret_val[-1]
            self.logger.info('outlook.unread: latest_id {0}'.format(latest_id))
            return self.get_email(latest_id)
        return ''

    def unread_after_date(self, inp_date):
        # qry_date = inp_date.strftime("%-d-%b-%Y")    # no leading zero in day
        qry_date = inp_date.strftime("%d-%b-%Y")
        print('qry_date:', qry_date)

        search_criteria = '(SINCE "{qry_date}")'.format(qry_date=qry_date)
        print('search_criteria:', search_criteria)

        typ, data = self.imap.search(None, search_criteria, 'ALL')
        print('typ:', typ)
        print('data:', data)
        search_result = data[0].decode('UTF-8')
        print('search_result:', 'xxx' + search_result + 'xxx')

        # if no messages (search_result has message ids) since input date return empty list
        str_ids = search_result.split(' ')
        msg_ids = [int(x) for x in str_ids]
        print('msg_ids:', msg_ids)

        stack = []
        for msg_id in msg_ids:
            self.get_email(msg_id)
            msg = {
                'msg_id': msg_id,
                'msg_body': self.mail_body(),
                'msg_subject': self.mail_subject(),
                'msg_date': self.mail_date(),
                'msg_from': self.mail_from(),
                'msg_to': self.mail_to()
            }
            stack.append(msg)
        return stack

    def unread_after_datetime(self, inp_datetime):
        # qry_date = inp_datetime.strftime("%d-%b-%Y")
        # qry_date = datetime.datetime.strptime(inp_datetime, '%Y-%m-%d').date()

        # get all unread messages after specified date
        # SINCE only accepts dates when querying mailbox
        msgs = self.unread_after_date(inp_datetime)

        # further filter by date time
        stack = list(filter(lambda x: x['msg_date'] >= inp_datetime, msgs))
        return stack

    def unread_ids(self):
        # https://tools.ietf.org/html/rfc3501#section-6.4.4
        # r, d = self.imap.search(None, "NEW")
        r, d = self.imap.search(None, "UNSEEN")

        # convert bytes to string
        ids = d[0].decode('UTF-8', 'replace')

        # if no unread messages return empty list
        ret_val = []
        if len(ids) > 0:
            ret_val = [ids]
            if ' ' in ids:
                ret_val = ids.split(' ')
        return ret_val

    def unread_ids_today(self):
        r, d = self.imap.search(None, '(SINCE "'+self.today+'")', 'UNSEEN')
        ret_val = d[0].split(' ')
        return ret_val

    def unread_today(self):
        ret_val = self.unread_ids_today()
        latest_id = ret_val[-1]
        return self.get_email(latest_id)

    def write_enable(self, folder):
        return self.imap.select(folder, readonly=False)
