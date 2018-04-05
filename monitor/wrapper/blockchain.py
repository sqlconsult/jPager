#!/usr/bin/env python3

import datetime
import hashlib
import json
import os

dt_fmt_str = '{dt:%Y-%m-%d %H:%M:%S}'


class BlockChain(object):
    def __init__(self, params, module_logger):
        self.chain = []
        self.current_transactions = []
        self.params = params

        # if block chain data file does not exist, create genesis block
        # print('BlockChain', params[0]['DataChain'])
        # print('BlockChain', os.getcwd())
        if not os.path.exists(params[0]['DataChain']):
            module_logger.info('Adding genesis block to data file {0}'.
                               format(params[0]['DataChain']))
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
        else:
            # read existing block chain into memory
            with open(params[0]['DataChain'], 'r') as handle:
                self.chain = json.load(handle)

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

    def full_chain(self):
        response = {
            'chain': self.chain,
            'length': len(self.chain),
        }
        return response

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

    def mine(self, node_identifier, module_logger):
        module_logger.info('===> Mine a block <===')
        # We run the proof of work algorithm to get the next proof...
        last_block = self.last_block
        last_proof = last_block['proof']

        proof = self.proof_of_work(last_proof)

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
        self.new_transaction(empty_block)

        # Forge the new Block by adding it to the chain
        # print('type(last_block):', type(last_block), 'last_block:', last_block)
        # module_logger.info('mine: hash last block')
        previous_hash = self.hash(last_block)
        # module_logger.info('mine: add mined block to chain')
        block = self.new_block(proof, previous_hash)

        # module_logger.info('mine: send response')
        response = {
            'message': 'New Block Forged',
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
        }
        return response, 200

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

        # add this block to both the data file and in memory chain
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
