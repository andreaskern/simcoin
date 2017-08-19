import config
import re
from datetime import datetime
import logging
import numpy as np
from utils import Stats
from collections import namedtuple


class Parser:
    def __init__(self, context):
        self.context = context
        self.nodes_create_blocks = {node.name: None for node in context.all_bitcoin_nodes.values()}

        self.parsers = [func for func in dir(Parser) if callable(getattr(Parser, func)) and func.endswith("_parser")]

    def execute(self):
        with open(config.aggregated_sim_log, 'r') as file:
            lines = file.readlines()
            for line in lines:
                for parser in self.parsers:
                    try:
                        self.execute_parser(parser, line)
                        break
                    except ParseException:
                        pass
        logging.info('Executed parser')

    def execute_parser(self, parser, line):
        getattr(Parser, parser)(self, line)

    def block_creation_parser(self, line):
        create_new_block = parse_create_new_block(line)

        self.nodes_create_blocks[create_new_block.node] = create_new_block

    def tip_updated_parser(self, line):
        update_tip = parse_update_tip(line)

        create_new_block = self.nodes_create_blocks[update_tip.node]
        if create_new_block is not None:
            block_stats = BlockStats(create_new_block.timestamp, create_new_block.node, update_tip.block_hash,
                                     create_new_block.total_size, create_new_block.txs)
            block_stats.height = update_tip.height
            self.context.parsed_blocks[update_tip.block_hash] = block_stats
            self.nodes_create_blocks[update_tip.node] = None
        else:
            if update_tip.block_hash in self.context.parsed_blocks:
                block_stats = self.context.parsed_blocks[update_tip.block_hash]
                block_stats.height = update_tip.height

    def block_received_parser(self, line):
        received_block = parse_received_block(line)

        block_stats = self.context.parsed_blocks[received_block.obj_hash]

        block_stats.receiving_timestamps = np.append(block_stats.receiving_timestamps,
                                                     received_block.timestamp - block_stats.timestamp)

    def block_reconstructed_parser(self, line):
        received_block = parse_successfully_reconstructed_block(line)

        block_stats = self.context.parsed_blocks[received_block.obj_hash]

        block_stats.receiving_timestamps = np.append(block_stats.receiving_timestamps,
                                                     received_block.timestamp - block_stats.timestamp)

    def tx_creation_parser(self, line):
        log_line_with_hash = parse_add_to_wallet(line)

        self.context.parsed_txs[log_line_with_hash.obj_hash] = TxStats(log_line_with_hash.timestamp,
                                                        log_line_with_hash.node, log_line_with_hash.obj_hash)

    def tx_received_parser(self, line):
        log_line_with_hash = parse_accept_to_memory_pool(line)

        tx_stats = self.context.parsed_txs[log_line_with_hash.obj_hash]
        tx_stats.receiving_timestamps = np.append(tx_stats.receiving_timestamps,
                                                  log_line_with_hash.timestamp - tx_stats.timestamp)

    def peer_logic_validation_parser(self, line):
        log_line_with_hash = parse_peer_logic_validation(line)
        create_new_block = self.nodes_create_blocks[log_line_with_hash.node]

        if create_new_block is not None:

            block_stats = BlockStats(create_new_block.timestamp, create_new_block.node, log_line_with_hash.obj_hash,
                                     create_new_block.total_size, create_new_block.txs)
            self.context.parsed_blocks[block_stats.block_hash] = block_stats
            self.nodes_create_blocks[log_line_with_hash.node] = None

    def checking_mempool_parser(self, line):
        checking_mempool_log_line = parse_checking_mempool(line)

        self.context.mempool_snapshots.append(checking_mempool_log_line)
    def tick_parser(self, line):
        self.context.tick_infos.append(
            parse_tick_log_line(line)
        )


def parse_create_new_block(line):
    regex = config.log_prefix_full + 'CreateNewBlock\(\): total size: ([0-9]+)' \
                                ' block weight: [0-9]+ txs: ([0-9]+) fees: [0-9]+ sigops [0-9]+$'
    matched = re.match(regex, line)

    if matched is None:
        raise ParseException("Didn't matched CreateNewBlock log line.")

    return CreateNewBlockLogLine(
        datetime.strptime(matched.group(1), config.log_time_format).timestamp(),
        str(matched.group(2)),
        int(matched.group(3)),
        int(matched.group(4)),
    )


def parse_update_tip(line):
    regex = config.log_prefix_full + 'UpdateTip: new best=([0-9,a-z]{64}) height=([0-9]+) version=0x[0-9]{8}' \
                                ' log2_work=[0-9]+\.?[0-9]* tx=([0-9]+)' \
                                ' date=\'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\'' \
                                ' progress=[0-9]+.[0-9]+ cache=[0-9]+\.[0-9]+[a-zA-Z]+\([0-9]+txo?\)$'
    matched = re.match(regex, line)

    if matched is None:
        raise ParseException("Didn't matched CreateNewBlock log line.")

    return UpdateTipLogLine(
        datetime.strptime(matched.group(1), config.log_time_format).timestamp(),
        str(matched.group(2)),
        str(matched.group(3)),
        int(matched.group(4)),
        int(matched.group(5)),
    )


def parse_received_block(line):
    regex = config.log_prefix_full + 'received block ([a-z0-9]{64}) peer=[0-9]+$'

    matched = re.match(regex, line)

    if matched is None:
        raise ParseException("Didn't matched Received block log line.")

    return LogLineWithHash(
        datetime.strptime(matched.group(1), config.log_time_format).timestamp(),
        str(matched.group(2)),
        str(matched.group(3)),
    )


def parse_successfully_reconstructed_block(line):
    regex = config.log_prefix_full + 'Successfully reconstructed block ([a-z0-9]{64}) ' \
                                     'with ([0-9]+) txn prefilled, ([0-9]+) txn from mempool' \
                                     ' \(incl at least ([0-9]+) from extra pool\) and [0-9]+ txn requested$'
    matched = re.match(regex, line)

    if matched is None:
        raise ParseException("Didn't matched Successfully reconstructed block log line.")

    return LogLineWithHash(
        datetime.strptime(matched.group(1), config.log_time_format).timestamp(),
        str(matched.group(2)),
        str(matched.group(3)),
    )


def parse_add_to_wallet(line):
    regex = config.log_prefix_full + 'AddToWallet ([a-z0-9]{64})  new$'

    matched = re.match(regex, line)

    if matched is None:
        raise ParseException("Didn't matched AddToWallet log line.")

    return LogLineWithHash(
        datetime.strptime(matched.group(1), config.log_time_format).timestamp(),
        str(matched.group(2)),
        str(matched.group(3)),
    )


def parse_accept_to_memory_pool(line):
    regex = config.log_prefix_full + 'AcceptToMemoryPool: peer=([0-9]+):' \
                                     ' accepted ([0-9a-z]{64}) \(poolsz ([0-9]+) txn,' \
                                     ' ([0-9]+) [a-zA-Z]+\)$'

    matched = re.match(regex, line)

    if matched is None:
        raise ParseException("Didn't matched AcceptToMemoryPool log line.")

    return LogLineWithHash(
        datetime.strptime(matched.group(1), config.log_time_format).timestamp(),
        str(matched.group(2)),
        str(matched.group(4)),
    )


def parse_peer_logic_validation(line):
    regex = config.log_prefix_full + 'PeerLogicValidation::NewPoWValidBlock ' \
                                     'sending header-and-ids ([a-z0-9]{64}) ' \
                                     'to peer=[0-9]+'
    matched = re.match(regex, line)

    if matched is None:
        raise ParseException("Didn't matched AcceptToMemoryPool log line.")

    return LogLineWithHash(
        datetime.strptime(matched.group(1), config.log_time_format).timestamp(),
        str(matched.group(2)),
        str(matched.group(3)),
    )


def parse_checking_mempool(line):
    regex = config.log_prefix_full + 'Checking mempool with ([0-9]+) transactions and ([0-9]+) inputs'

    matched = re.match(regex, line)

    if matched is None:
        raise ParseException("Didn't matched AcceptToMemoryPool log line.")

    return CheckingMempoolLogLine(
        datetime.strptime(matched.group(1), config.log_time_format).timestamp(),
        str(matched.group(2)),
        int(matched.group(3)),
        int(matched.group(4)),
    )


def parse_tick_log_line(line):
    regex = config.log_prefix_full + '\[.*\] \[.*\]  Sleep ([0-9]+\.[0-9]+) seconds for next tick.$'

    matched = re.match(regex, line)

    if matched is None:
        raise ParseException("Didn't matched tick log line.")

    return TickLogLine(
        datetime.strptime(matched.group(1), config.log_time_format).timestamp(),
        float(matched.group(3)),
    )

LogLine = namedtuple('LogLine', 'timestamp node')

TickLogLine = namedtuple('TickLogLine', 'timestamp sleep_time')

CreateNewBlockLogLine = namedtuple('CreateNewBlockLogLine', 'timestamp node  total_size txs')

UpdateTipLogLine = namedtuple('UpdateTipLogLine', 'timestamp node block_hash height tx')

LogLineWithHash = namedtuple('LogLineWithHash', 'timestamp node obj_hash')

CheckingMempoolLogLine = namedtuple('CheckingMempoolLogLine', 'timestamp node txs inputs')


class BlockStats:
    def __init__(self, timestamp, node, block_hash, total_size, txs):
        self.timestamp = timestamp
        self.node = node
        self.block_hash = block_hash
        self.total_size = total_size
        self.txs = txs
        self.height = -1
        self.receiving_timestamps = np.array([])


class TxStats:

    def __init__(self, timestamp, node, tx_hash):
        self.timestamp = timestamp
        self.node = node
        self.tx_hash = tx_hash
        self.receiving_timestamps = np.array([])


class ParseException(Exception):
    pass
