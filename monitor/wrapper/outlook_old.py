#!/usr/bin/env python3

#
# TODO: Implement logging in place of print (line 57)
#

import email
import imaplib
import smtplib
import datetime
import email.mime.multipart
import base64

import wrapper.outlook_config as config


#########################################################################
#             From: https://github.com/awangga/outlook                  #
#                                                                       #
#    https://tools.ietf.org/html/rfc3501#section-6.4.4                  #
#                                                                       #
#########################################################################
class MailMsg:
    def __init__(self, mail_to, mail_from, mail_subject, mail_datetime, mail_body):
        self.mail_to = mail_to
        self.mail_from = mail_from
        self.mail_subject = mail_subject
        self.mail_datetime = mail_datetime
        self.mail_body = mail_body


class Outlook:

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

    def __init__(self):
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
                print('Connection attempt {num_try} of {max_try}'.\
                      format(num_try=num_try, max_try=max_try))
            num_try += 1

        # self.imap = imaplib.IMAP4_SSL('imap-mail.outlook.com')
        # self.smtp = smtplib.SMTP('smtp-mail.outlook.com')

    def login(self, username, password):
        self.username = username
        self.password = password
        while True:
            try:
                self.imap = imaplib.IMAP4_SSL(config.imap_server, config.imap_port)
                r, d = self.imap.login(username, password)
                assert r == 'OK', 'login failed'
                # print(" > Signed in as ", d)
                return True
            except:
                # print(" > Sign in failed...")
                return False

    def sendEmailMIME(self, recipient, subject, message):
        msg = email.mime.multipart.MIMEMultipart()
        msg['to'] = recipient
        msg['from'] = self.username
        msg['subject'] = subject
        msg.add_header('reply-to', self.username)
        # headers = "\r\n".join(["from: " + "sms@kitaklik.com","subject: " + subject,"to: " + recipient,"mime-version: 1.0","content-type: text/html"])
        # content = headers + "\r\n\r\n" + message
        try:
            self.smtp = smtplib.SMTP(config.smtp_server, config.smtp_port)
            self.smtp.ehlo()
            self.smtp.starttls()
            self.smtp.login(self.username, self.password)
            self.smtp.sendmail(msg['from'], [msg['to']], msg.as_string())
            print("email sent")
            return True
        except smtplib.SMTPException:
            # print("Error: unable to send email")
            return False

    def sendEmail(self, recipient, subject, message):
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
                print("email sent")
                return True
            except:
                print("Failed sending email...")
                return False

    # def list(self):
    #     # self.login()
    #     return self.imap.list()

    def select(self, str):
        return self.imap.select(str)

    def inbox(self):
        return self.imap.select("Inbox")

    def junk(self):
        return self.imap.select("Junk")

    def logout(self):
        return self.imap.logout()

    def today(self):
        mydate = datetime.datetime.now()
        return mydate.strftime("%d-%b-%Y")

    def unreadIdsAfter(self, recv_dt):
        qry_date = recv_dt.strftime("%d-%b-%Y")
        # print('qry_date:', qry_date)

        search_criteria = '(SINCE "{qry_date}")'.format(qry_date=qry_date)
        # print('search_criteria:', search_criteria)

        r, d = self.imap.search(None, search_criteria, 'ALL')
        search_result = d[0].decode('UTF-8')
        # print('search_result:', 'xxx' + search_result + 'xxx')

        # if no messages (search_result has message ids) since input date return empty list
        msg_ids = search_result.split(' ')
        # msg_ids = [int(x) for x in str_ids]
        # print('msg_ids:', msg_ids)

        stack = []
        for msg_id in msg_ids:
            msg = self.getEmail(msg_id)
            msg_body = self.mailbody()
            msg_subject = self.mailsubject()
            msg_date = self.maildate()
            msg_from = self.mailfrom()
            msg_to = self.mailto()
            tmp_msg = MailMsg(msg_to, msg_from, msg_subject, msg_date, msg_body)
            stack.append(tmp_msg)
        return stack

    def unreadIdsToday(self):
        r, d = self.imap.search(None, '(SINCE "'+self.today+'")', 'UNSEEN')
        ret_val = d[0].split(' ')
        return ret_val

    def getIdswithWord(self, ids, word):
        stack = []
        for id in ids:
            self.getEmail(id)
            if word in self.mailbody().lower():
                stack.append(id)
        return stack

    def unreadIds(self):
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

    def hasUnread(self):
        ret_val = self.unreadIds()
        return ret_val != []

    def readIdsToday(self):
        r, d = self.imap.search(None, '(SINCE "'+self.today+'")', 'SEEN')
        ret_val = d[0].split(' ')
        return ret_val

    def allIds(self):
        r, d = self.imap.search(None, "ALL")
        ret_val = d[0].split(' ')
        return ret_val

    def readIds(self):
        r, d = self.imap.search(None, "SEEN")
        ret_val = d[0].split(' ')
        return ret_val

    def getEmail(self, msg_id):
        r, d = self.imap.fetch(msg_id, "(RFC822)")

        raw_email = d[0][1].decode('UTF-8', 'replace')

        # print('getEmail: raw_email:', raw_email)
        self.raw_email = raw_email
        self.email_message = email.message_from_string(self.raw_email)
        return self.email_message

    def unread(self):
        ret_val = self.unreadIds()
        if ret_val:
            latest_id = ret_val[-1]
            print('unread: latest_id:', latest_id)
            return self.getEmail(latest_id)
        return ''

    def read(self):
        ret_val = self.readIds()
        latest_id = ret_val[-1]
        return self.getEmail(latest_id)

    def readToday(self):
        ret_val = self.readIdsToday()
        latest_id = ret_val[-1]
        return self.getEmail(latest_id)

    def unreadToday(self):
        ret_val = self.unreadIdsToday()
        latest_id = ret_val[-1]
        return self.getEmail(latest_id)

    def readOnly(self, folder):
        return self.imap.select(folder, readonly=True)

    def writeEnable(self, folder):
        return self.imap.select(folder, readonly=False)

    def rawRead(self):
        ret_val = self.readIds()
        latest_id = ret_val[-1]
        r, d = self.imap.fetch(latest_id, "(RFC822)")
        self.raw_email = d[0][1]
        return self.raw_email

    def mailbody(self):
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

    def maildate(self):
        return self.email_message['Date']

    def mailsubject(self):
        return self.email_message['Subject']

    def mailfrom(self):
        return self.email_message['from']

    def mailto(self):
        return self.email_message['to']

    def mailreturnpath(self):
        return self.email_message['Return-Path']

    def mailreplyto(self):
        return self.email_message['Reply-To']

    def mailall(self):
        return self.email_message

    def mailbodydecoded(self):
        return base64.urlsafe_b64decode(self.mailbody())
