import config
import logging
from utils import Stats
import csv
import json


class Analyzer:
    def __init__(self, context):
        self.context = context

    def execute(self):
        funcs = [func for func in dir(Analyzer) if callable(getattr(Analyzer, func)) and func.startswith('create_')]

        for func in funcs:
            getattr(Analyzer, func)(self)

        logging.info('Executed {} functions during execution of analyzer'.format(len(funcs)))

    def create_block_csv(self):
        with open(config.blocks_csv, 'w') as file:
            w = csv.writer(file, delimiter=';')
            w.writerow(['block_hash', 'node', 'timestamp', 'stale', 'height', 'total_size', 'txs',
                        'received_by', 'median_propagation', 'std_propagation'])
            for block in self.context.parsed_blocks.values():

                propagation_stats = Stats.from_array(block.receiving_timestamps)

                stale = 'Stale'
                if block.block_hash in self.context.consensus_chain:
                    stale = 'Accepted'

                w.writerow([block.block_hash, block.node, block.timestamp, stale, block.height, block.total_size,
                            block.txs, propagation_stats.count, propagation_stats.median, propagation_stats.std])

    def create_tx_csv(self):
        with open(config.txs_csv, 'w') as file:
            w = csv.writer(file, delimiter=';')
            w.writerow(['tx_hash', 'node', 'timestamp', 'accepted_by', 'median_propagation', 'std_propagation'])

            for tx in self.context.parsed_txs.values():
                propagation_stats = Stats.from_array(tx.receiving_timestamps)

                w.writerow([tx.tx_hash, tx.node, tx.timestamp,
                            propagation_stats.count, propagation_stats.median, propagation_stats.std])

    def create_tx_exceptions_csv(self):
        with open(config.tx_exceptions_csv, 'w') as file:
            w = csv.writer(file, delimiter=';')
            w.writerow(['node', 'timestamp', 'exception'])

            for exce in self.context.tx_exceptions:
                w.writerow([exce.node, exce.timestamp, exce.exception])

    def create_block_exceptions_csv(self):
        with open(config.block_exceptions_csv, 'w') as file:
            w = csv.writer(file, delimiter=';')
            w.writerow(['node', 'timestamp', 'exception'])

            for exce in self.context.block_exceptions:
                w.writerow([exce.node, exce.timestamp, exce.exception])

    def create_tick_infos_csv(self):
        with open(config.tick_infos_csv, 'w') as file:
            w = csv.writer(file, delimiter=';')
            w.writerow(['timestamp', 'start', 'duration'])

            for tick in self.context.tick_infos:
                w.writerow([tick.timestamp, tick.start, tick.duration])

    def create_mempool_snapshots_csv(self):
        with open(config.mempool_snapshots_csv, 'w') as file:
            w = csv.writer(file, delimiter=';')
            w.writerow(['timestamp', 'node', 'txs', 'inputs'])

            for snapshot in self.context.mempool_snapshots:
                w.writerow([snapshot.timestamp, snapshot.node, snapshot.txs, snapshot.inputs])

    def create_rpc_exceptions_csv(self):
        with open(config.rpc_exceptions_csv, 'w') as file:
            w = csv.writer(file, delimiter=';')
            w.writerow(['timestamp', 'node', 'method', 'exception'])

            for exce in self.context.rpc_exceptions:
                w.writerow([exce.timestamp, exce.node, exce.method, exce.exception])


def create_general_infos_json(general_infos):
    with open(config.general_infos_json, 'w') as file:
        file.write('{}\n'.format(json.dumps(general_infos)))
