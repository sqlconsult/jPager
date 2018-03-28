#!/usr/bin/env python3
import json
import logging

import run.model as model
import wrapper.logger as logger
import wrapper.sendmail as sendmail


def main():
    # Start logger
    app_name = __file__.split('.')[0]
    logger.start_logger(app_name)

    module_logger = logging.getLogger('{app_name}.controller'.format(app_name=app_name))
    module_logger.info('===== Starting =====')

    # Get and log input parameters
    module_logger.info('Parameters:')
    params = read_params()

    module_logger.info(json.dumps(params, indent=4, sort_keys=True))

    return_status = monitor_loop(params, module_logger)
    return_status = True

    if return_status:
        module_logger.info('Successful')
    else:
        module_logger.error("Failed")

    module_logger.info('===== Stopping =====')


def monitor_loop(params, module_logger):
    # check mailbox to monitor credentials
    email_id = params[0]['MailBoxToMonitor']    # mailbox =_maint@outlook.com
    email_pwd = params[0]['MailBoxPassword']    # pwd = Byte1234
    return_status = sendmail.check_credentials(email_id, email_pwd)
    if not return_status:
        module_logger.error('Failed credential check for {mbx}'.format(mbx=email_id))
        return False

    # read existing open transactions from block chain / mongo database (transactions)
    existing_alerts = model.get_existing_alerts(params)

    module_logger.info('monitor_loop: Retrieved {0} open alerts'.
                       format(len(existing_alerts)))
    return True


def read_params():
    with open('./params.json', 'r') as handle:
        json_params = json.load(handle)
    return json_params


if __name__ == '__main__':
    main()
