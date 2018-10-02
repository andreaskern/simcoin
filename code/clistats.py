import logging
from bitcoin.rpc import JSONRPCError
from setuptools.package_index import unique_everseen

import utils
import config
from operator import attrgetter


class CliStats:
    def __init__(self, context, writer):
        self._context = context
        self._writer = writer

    def execute(self):
        height = self._context.first_block_height
        nodes = self._context.nodes.values()

        if(height == None):
            height = 0

        _persist_consensus_chain(self._calc_consensus_chain(height, nodes))
        self._persist_node_stats()
        self._collect_forks_form_getchaintips()  # TODO fix headers

        logging.info('Executed cli stats')

    def _calc_consensus_chain(self, height, nodes):
        consensus_chain = []
        logging.info('Calculating consensus chain starting with height={}'.format(height))
        while True:
            block_hashes = {}
            failing_nodes = []
            block_hash = None
            for node in nodes:
                try:
                    block_hash = node.execute_rpc('getblockhash', height)
                    if block_hash in block_hashes:
                        block_hashes[block_hash].append(node.name)
                    else:
                        block_hashes[block_hash] = [node.name]
                except JSONRPCError:
                    failing_nodes.append(node.name)
            if len(failing_nodes) > 0:
                logging.info('Stopped calculating consensus chain on height={} because nodes={}'
                             ' have no block on this height'.format(height, failing_nodes))
                break
            elif len(block_hashes) > 1:
                logging.info('Stopped calculating consensus chain on height={} because'
                             ' nodes have different blocks ({})'.format(height, block_hashes))
                break
            else:
                consensus_chain.append(block_hash)
                height += 1

                logging.info('Added block with hash={} to consensus chain'.format(block_hash))

        logging.info('Calculated {} block long consensus chain from {} nodes and until height={}'
                     .format(len(consensus_chain), len(nodes), height - 1))
        return consensus_chain

    def _persist_node_stats(self):  # forks calculated here
        tips = []
        for node in self._context.nodes.values():
            tips.extend(
                    [
                        Tip.from_dict(
                            node.name,
                            chain_tip
                        )
                        for chain_tip
                        in node.execute_rpc('getchaintips')
                     ]
            )

        self._writer.write_csv(
                Tip.file_name,
                Tip.csv_header,
                tips
        )
        logging.info('Collected and persisted {} tips'.format(len(tips)))

    def _collect_forks_form_getchaintips(self):
        self.__collect_forks_form_getchaintips(
            self._context.nodes.values(),
            self._writer
        )


    @staticmethod
    def __collect_forks_form_getchaintips(node_values, writer):
        logging.info('Collecting forks.csv from getchaintips')

        tips = []
        for node in node_values:
            tips.extend(
                    [
                        Tip.from_dict(
                                node.name,
                                chain_tip
                        )
                        for chain_tip
                        in node.execute_rpc('getchaintips')
                    ]
            )

        '''
    
        Possible values for status:
        1.  "invalid"         branch contains invalid blocks
        2.  "headers-only"    Not all blocks for this branch are available, but the headers are valid
        3.  "valid-headers"   All blocks are available for this branch, but they were never fully validated
        4.  "valid-fork"            This branch is not part of the active chain, but is fully validated
        5.  "active"                This is the tip of the active main chain, which is certainly valid
        
        fork life cycle
        
        headers-only -> valid.headers -> {invalid, valid-fork -> active -> [REC:valid-fork]}
    
        '''
        forks = []

        '''select height, status '''
        for tip in tips:
            forks.extend([
                tip._height,
                tip._status
            ])

        '''filter status != valid-fork'''
        forks = [tip for tip in tips if tip.is_valid_fork()]

        '''aggregate by hash # fold status '''
        forks = unique_everseen(forks, key=attrgetter('_hash'))

        '''sort by tag, height'''
        forks = sorted(forks, key=attrgetter('_height'))
        # sorted(forks, key=attrgetter('_tag')) # tag is added later

        writer.write_csv(
                "forks.csv",
                ['node','status','length','height', 'tag'],
                forks
        )


def _persist_consensus_chain(chain):
    with open(config.consensus_chain_csv, 'w') as file:
        file.write('hash\n')
        file.writelines('\n'.join(chain))
        file.write('\n')


class Tip:
    __slots__ = ['_node', '_status', '_branchlen', '_height', '_hash']
    csv_header = ['node', 'status', 'branchlen', 'height', 'hash']

    file_name = 'tips.csv'

    def __init__(self, node, status, branchlen, height, hash):
        self._node = node
        self._status = status
        self._branchlen = branchlen
        self._height = height
        self._hash = hash

    def is_valid_fork(self) -> bool:
        return self._status == 'valid-fork'

    @classmethod
    def from_dict(cls, node, chain_tip):
        return cls(
                node,
                chain_tip['status'],
                chain_tip['branchlen'],
                chain_tip['height'],
                chain_tip['hash']
        )

    def vars_to_array(self):
        return [
            self._node,
            self._status,
            self._branchlen,
            self._height,
            self._hash
        ]
