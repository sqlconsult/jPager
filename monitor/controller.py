#!/usr/bin/env python3
import datetime
import json
import logging
# import os
import pprint

import run.model as model
import wrapper.logger as logger
import wrapper.credentials as cred
import wrapper.blockchain as bc


def main():
    # Start logger
    app_name = __file__.split('.')[0]
    logger.start_logger(app_name)

    module_logger = logging.getLogger('{app_name}.controller'.format(app_name=app_name))
    module_logger.info('===== Starting =====')

    # Get and log input parameters
    params = read_params()
    module_logger.info('Parameters:')
    module_logger.info(json.dumps(params, indent=4, sort_keys=True))

    return_status = monitor_loop(params, module_logger)

    if return_status:
        module_logger.info('Successful')
    else:
        module_logger.error("Failed")

    module_logger.info('===== Stopping =====')


def monitor_loop(params, module_logger):
    # Instantiate our Block chain including a genesis block
    # print('monitor_loop', params[0]['DataChain'])
    # print('monitor_loop', os.getcwd())
    block_chain = bc.BlockChain(params, module_logger)

    response = block_chain.full_chain()
    alerts = response['chain']

    # print(response['length'])
    # print(type(alerts))
    # print(alerts)

    # read block chain alerts and leave only open alerts in a dictionary
    #     str_dt = datetime.datetime.strftime(alert['notification_dt'], '%Y%m%d_%H%M%S')
    #     key = '{0}~{1}~{2}~{3}'.\
    #             format(alert['job_name'], alert['email_from'], alert['response_order'], str_dt)
    open_alerts = model.get_existing_open_alerts(alerts, module_logger)

    # for k, v in open_alerts.items():
    #     print('Key: {key}\n    {value}'.format(key=k, value=v))

    ref_data = model.get_ref_data(params)
    module_logger.info('monitor_loop: Retrieved {0} reference data records'.format(len(ref_data)))

    # module_logger.info('ref_data')
    # pp = pprint.PrettyPrinter(indent=4)
    # s = pp.pformat(ref_data)
    # module_logger.info('monitor_loop:{0}'.format(s))

    ret_sts = model.escalate_job_alerts(open_alerts, ref_data, module_logger, cred.creds)

    # While not params.quit and Now <= Midnight Today
    #
    #    Get messages from MailboxToMonitor after Date(LastTimeChecked)
    #    Sort retrieved messages by message id
    #    For msg in messages:
    #        Extract from, date time, subject and to from msgs
    #        Convert msg date time from string to datetime

    now = datetime.datetime.now()
    midnight = datetime.datetime(now.year, now.month, now.day, 23, 59, 59)

    while params['quit'][1].upper() != 'Q' and now < midnight:

        now = datetime.datetime.now()
        pass

    return ret_sts


def read_params():
    with open('./params.json', 'r') as handle:
        json_params = json.load(handle)
    return json_params


if __name__ == '__main__':
    main()
