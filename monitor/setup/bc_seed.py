#!/usr/bin/env python3

import csv
import datetime
from dateutil.parser import parse
import hashlib
import json
import logging
import os
import pprint
# from uuid import uuid4     # used to mine a block

dt_fmt_str = '{dt:%Y-%m-%d %H:%M:%S}'


class BlockChain(object):
    def __init__(self, params):
        self.chain = []
        self.current_transactions = []
        self.params = params

        # Create the genesis block
        genesis = {
            'dept_name': 'jedi',
            'job_name': 'Use The Force',
            'user_name': 'n_kata_del_gormo',
            'email_subject': 'The Force Awakens',
            'email_from': 'n_kata_del_gormo',
            'email_to': 'yoda',
            'sla_time': 999,
            'response_order': 1,
            'notification_dt': dt_fmt_str.format(dt=datetime.datetime(2018, 1, 1, 0, 0, 1)),
            'response_dt': dt_fmt_str.format(dt=datetime.datetime(2018, 1, 1, 23, 59, 59))
        }
        proof = self.proof_of_work(100)

        self.new_transaction(genesis)

        # no previous block to hash
        previous_hash = 1

        # add this block to the chain
        self.new_block(proof, previous_hash)
        # self.new_block(proof=100, previous_hash=1)

    def append_block_to_file(self, block):
        # append this block to the block chain data file
        fil_nm = self.params[0]['DataChain']
        tmp_chain = []

        if os.path.exists(fil_nm):
            # if the block chain data file exists read it into memory
            with open(fil_nm, mode='r+', encoding='utf-8') as f:
                tmp_chain = json.load(f)
        else:
            # create the file
            with open(fil_nm, mode='w+', encoding='utf-8'):
                pass

        # append new block
        tmp_chain.append(block)

        # re-write block chain data file
        with open(fil_nm, mode='w', encoding='utf-8') as f:
            f.write(json.dumps(tmp_chain, indent=4, sort_keys=True))

    @staticmethod
    def hash(block):
        # neither self (the object instance) nor cls (the class)
        # is implicitly passed as the first argument
        #
        # Hashes a Block
        """
               Creates a SHA-256 hash of a Block
               :param block: <dict> Block
               :return: <str>
        """
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes
        # print('hash: block:', block)
        block_string = json.dumps(block, sort_keys=True).encode()
        # print('hash: block_string:', block_string)

        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Returns the last Block in the chain
        return self.chain[-1]

    def new_block(self, proof, previous_hash=None):
        # Creates a new Block and adds it to the chain
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': dt_fmt_str.format(dt=datetime.datetime.now()),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)

        self.append_block_to_file(block)

        return block

    def new_transaction(self, item_to_add):
        # Adds a new transaction to the list of transactions
        """
        Creates a new transaction to go into the next mined Block
            item_to_add = {
            'dept_name': 'jedi',
            'job_name': 'Use The Force',
            'user_name': 'n_kata_del_gormo',
            'email_subject': 'The Force Awakens',
            'email_from': 'n_kata_del_gormo',
            'email_to': 'yoda',
            'sla_time': 999,
            'response_order': 1,
            'notification_dt': datetime.datetime(2018, 1, 1, 0, 0, 1),
            'response_dt': datetime.datetime(2018, 1, 1, 23, 59, 59) }
            :return: <int> The index of the Block that will hold this transaction
        """

        self.current_transactions.append(item_to_add)

        return 0 if len(self.chain) == 0 else self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """
        proof = last_proof
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain n leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """
        n = 2
        guess = str(last_proof * proof)
        guess_hash = hashlib.sha256(guess.encode()).hexdigest()
        return guess_hash[:n] == n * '0'


def full_chain(block_chain):
    response = {
        'chain': block_chain.chain,
        'length': len(block_chain.chain),
    }
    return response


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

    # creating new seed data, if block chain data file exists delete it
    if os.path.exists(json_params[0]['DataChain']):
        module_logger.info('Existing block chain data file {0} will be deleted'.
                           format(json_params[0]['DataChain']))
        os.remove(json_params[0]['DataChain'])

    # read test data into list of dictionary's
    test_xcns = read_test_transactions('Alerts.csv')
    module_logger.info('Read {0} test transactions'.format(len(test_xcns)))

    # Instantiate our Block chain including a genesis block
    block_chain = BlockChain(json_params)

    # response = {
    #     'chain': block_chain.chain,
    #     'length': len(block_chain.chain),
    # }
    #
    # module_logger.info('===> Display full chain <===')
    # module_logger.info(response['chain'])
    # s = pp.pformat(response['chain'])
    # module_logger.info('Chain [{0}]: {1}'.format(response['length'], s))

    # Generate a globally unique address for this node
    # A UUID (Universal Unique Identifier) is a 128-bit number used to uniquely
    # identify some object or entity on the Internet.
    # node_identifier = str(uuid4()).replace('-', '')

    # mine a block
    #
    # mined_block, ret_sts = mine(block_chain, node_identifier, module_logger)
    # pp_mined_block = pp.pformat(mined_block)
    # module_logger.info(pp_mined_block)

    # seed xcn block chain with some test data
    for alert in test_xcns:
        # get last block in chain
        last_block = block_chain.last_block

        # get last proof of work & calculate next proof of work
        last_proof = last_block['proof']
        proof = block_chain.proof_of_work(last_proof)

        # get next index in the chain
        # module_logger.info('===> Create a new transaction <===')
        # module_logger.info(response)
        # module_logger.info('===>')
        block_chain.new_transaction(alert)

        # hash previous block
        previous_hash = block_chain.hash(last_block)

        # add this block to the  hain
        block_chain.new_block(proof, previous_hash)

        # response = {'message': 'Transaction will be added to Block {index}'.format(index=index)}
        # s = pp.pformat(response)
        # module_logger.info('Transaction will be added to Block {index}'.format(index=index))

    # Display full chain
    response = {
        'chain': block_chain.chain,
        'length': len(block_chain.chain),
    }

    module_logger.info('===> Display full chain <===')
    # module_logger.info(response['chain'])
    s = pp.pformat(response['chain'])
    module_logger.info('Chain [{0}]:\n {1}'.format(response['length'], s))
    module_logger.info('===== Done =====')
    return True


def mine(block_chain, node_identifier, module_logger):
    module_logger.info('===> Mine a block <===')
    # We run the proof of work algorithm to get the next proof...
    last_block = block_chain.last_block
    last_proof = last_block['proof']

    proof = block_chain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The user_name, email_from and email_to = 'yoda' to signify that
    # this node has mined a new block.
    # module_logger.info('mine: set alert block variables')

    # '{date:%Y%m%d_%H%M%S}'.format(date=x)

    empty_block = {
        'dept_name': 'jedi',
        'job_name': node_identifier,
        'user_name': 'yoda',
        'email_subject': 'Use The Force',
        'email_from': 'yoda',
        'email_to': 'luke',
        'sla_time': 999,
        'response_order': 1,
        'notification_dt': '{dt:%Y-%m-%d %H:%M:%S}'.format(dt=datetime.datetime(2018, 1, 1, 0, 0, 1)),
        'response_dt': '{dt:%Y-%m-%d %H:%M:%S}'.format(dt=datetime.datetime(2018, 1, 1, 23, 59, 59))
    }

    # module_logger.info('mine: add new transaction')
    block_chain.new_transaction(empty_block)

    # Forge the new Block by adding it to the chain
    # print('type(last_block):', type(last_block), 'last_block:', last_block)
    # module_logger.info('mine: hash last block')
    previous_hash = block_chain.hash(last_block)
    # module_logger.info('mine: add mined block to chain')
    block = block_chain.new_block(proof, previous_hash)

    # module_logger.info('mine: send response')
    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return response, 200


def read_test_transactions(inp_file_path):

    # genesis entry
    alerts = []

    # read test data and return in a list of dictionary's
    with open(inp_file_path) as f:
        # read csv test data into a dictionary
        reader = csv.DictReader(f)
        rows = list(reader)

        # convert input strings to integers and date times
        for row in rows:
            new_dict = {
                'dept_name': row['dept_name'],
                'job_name': row['job_name'],
                'user_name': row['user_name'],
                'email_subject': row['email_subject'],
                'email_from': row['email_from'],
                'email_to': row['email_to'],
                'sla_time': int(row['sla_time']),
                'response_order': int(row['response_order'])}

            # if there's a notification datetime convert it to datetime
            # then, format it into a consistent format
            if len(row['notification_dt']) > 0:
                notify_dt = parse(row['notification_dt'])
                new_dict['notification_dt'] = dt_fmt_str.format(dt=notify_dt)

            # do same thing for response datetime
            if len(row['response_dt']) > 0:
                resp_dt = parse(row['response_dt'])
                new_dict['response_dt'] = dt_fmt_str.format(dt=resp_dt)

            alerts.append(new_dict)

    return alerts


def start_logger(logger):
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
    logger.addHandler(fh)
    logger.addHandler(ch)


if __name__ == '__main__':
    main()
