#!/usr/bin/env python3
import json
import logging
import os
import pprint

import run.model as model
import wrapper.logger as logger
import wrapper.sendmail as sendmail
import wrapper.blockchain as bc


def check_credentials(params, module_logger):
    # check mailbox to monitor credentials
    email_id = params[0]['MailBoxToMonitor']    # mailbox =_maint@outlook.com
    email_pwd = params[0]['MailBoxPassword']    # pwd = Byte1234
    return_status = sendmail.check_credentials(email_id, email_pwd)
    if not return_status:
        module_logger.error('Failed credential check for {mbx}'.format(mbx=email_id))
        return False
    return True


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
    # if not check_credentials(params, module_logger):
    #     return False

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
    #         key = '{0}~{1}~{2}~{3}'.\
    #             format(alert['job_name'], alert['email_from'], alert['response_order'], str_dt)
    open_alerts = model.get_existing_open_alerts(alerts, module_logger)
    module_logger.info('monitor_loop: Retrieved {0} open alerts'.format(len(open_alerts)))

    pp = pprint.PrettyPrinter(indent=4)
    s = pp.pformat(open_alerts)
    print('{0}'.format(s))

    ref_data = model.get_ref_data(params)
    module_logger.info('monitor_loop: Retrieved {0} reference data records'.format(len(ref_data)))

    # pp = pprint.PrettyPrinter(indent=4)
    # s = pp.pformat(ref_data)
    # module_logger.info('monitor_loop:{0}'.format(s))

    # TODO model.escalate_job_alerts(open_alerts, ref_data, params)

    return True


def read_params():
    with open('./params.json', 'r') as handle:
        json_params = json.load(handle)
    return json_params


if __name__ == '__main__':
    main()
