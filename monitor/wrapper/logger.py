#!/usr/bin/env python3

import datetime
import logging

# import auxiliary as auxiliary_module


def start_logger(app_name):
    # Create logger with 'spam_application'
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)

    # Create file handler which logs debug messages
    log_fil_nm = 'logs/monitor_log_{date:%Y%m%d_%H%M%S}.log'.format(date=datetime.datetime.now())
    fh = logging.FileHandler(log_fil_nm)
    fh.setLevel(logging.DEBUG)

    # Create console handler with a higher log level, error
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                                  datefmt="%Y-%m-%d %H:%M:%S")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    # for i in range(5):
    #     logger.error("{0} error...".format(i))
    #
    # logger.info('creating an instance of auxiliary_module.Auxiliary')
    # a = auxiliary_module.Auxiliary(app_name)
    #
    # logger.info('created an instance of auxiliary_module.Auxiliary')
    # logger.info('calling auxiliary_module.Auxiliary.do_something')
    # a.do_something()
    #
    # logger.info('finished auxiliary_module.Auxiliary.do_something')
    # logger.info('calling auxiliary_module.some_function()')
    # auxiliary_module.setup(app_name)
    # auxiliary_module.some_function()
    #
    # logger.info('done with auxiliary_module.some_function()')



"""

import logging

# Create logger
module_logger = logging.getLogger('app_nm.auxiliary')


class Auxiliary:
    def __init__(self, app_name):
        self.logger = logging.getLogger('{app_name}.auxiliary.Auxiliary'.format(app_name=app_name))
        self.logger.info('creating an instance of Auxiliary')

    def do_something(self):
        self.logger.info('doing something')
        a = 1 + 1
        self.logger.info('done doing something')


def setup(app_name):
    module_logger = logging.getLogger('{app_name}.auxiliary'.format(app_name=app_name))


def some_function():
    module_logger.info('received a call to "some_function"')


"""