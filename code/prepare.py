import config
import logging
import bash
from cmd import dockercmd
import os
import utils
import math
from multiprocessing.dummy import Pool as ThreadPool
import itertools
from bitcoin.rpc import DEFAULT_HTTP_TIMEOUT
import node as node_utils


class Prepare:
    def __init__(self, context):
        self._context = context
        # self._pool = None
    
    def create_folder(self):
        with ThreadPool(1) as pool:
            self._prepare_simulation_dir(pool)


    def execute(self):
        # self._pool = ThreadPool(5)

        with ThreadPool(1) as pool:
            logging.info('Begin of prepare step')

            # self._prepare_simulation_dir(pool)

            _remove_old_containers_if_exists()
            _recreate_network()

            # TODO fix negative coinbase transfers
            self._give_nodes_spendable_coins(pool)
            self._start_nodes(pool)

            # self._pool.close()

        logging.info('End of prepare step')

    def _prepare_simulation_dir(self, threadpool):
        if not os.path.exists(self._context.run_dir):
            os.makedirs(self._context.run_dir)

        if os.path.islink(config.soft_link_to_run_dir):
            bash.check_output('unlink {}'.format(config.soft_link_to_run_dir))
        bash.check_output('cd {}; ln -s {} {}'.format(config.data_dir, self._context.run_name, config.last_run))
        os.makedirs(config.postprocessing_dir)

        for file in [config.network_csv_file_name, config.ticks_csv_file_name,
                     config.nodes_csv_file_name, config.args_csv_file_name]:
            bash.check_output('cp {}{} {}'.format(config.data_dir, file, self._context.run_dir))
            bash.check_output('cd {}; ln -s ../{} {}'.format(config.postprocessing_dir, file, file))

        os.makedirs(config.node_config)
        threadpool.map(node_utils.create_conf_file, self._context.nodes.values())

        logging.info('Simulation directory created')

    def _give_nodes_spendable_coins(self, threadpool):
        nodes = list(self._context.nodes.values())
        cbs = []
        for i, node in enumerate(nodes):
            cbs.append(
                threadpool.apply_async(
                    node_utils.start_node,
                    args=(node, (str(node.ip) for node in nodes[max(0, i - 5):i]))
                )
            )
        for cb in cbs:
            cb.get()

        threadpool.map(node_utils.check_startup_node, nodes)

        amount_of_tx_chains = _calc_number_of_tx_chains(
            self._context.args.txs_per_tick,
            self._context.args.blocks_per_tick,
            len(nodes)
        )
        logging.info('Each node receives {} tx-chains'.format(amount_of_tx_chains))

        for i, node in enumerate(nodes):
            node_utils.wait_until_height_reached(node, i * amount_of_tx_chains)
            node.execute_rpc('generate', amount_of_tx_chains)
            logging.info('Generated {} blocks for node={} for their tx-chains'.format(amount_of_tx_chains, node.name))

        node_utils.wait_until_height_reached(nodes[0], amount_of_tx_chains * len(nodes))
        nodes[0].generate_blocks(config.blocks_needed_to_make_coinbase_spendable)
        current_height = config.blocks_needed_to_make_coinbase_spendable + amount_of_tx_chains * len(nodes)

        threadpool.starmap(node_utils.wait_until_height_reached, zip(nodes, itertools.repeat(current_height)))

        # TODO fix coinbase behaviour where [Example1](#AppendixA) does not occur
        # self._pool.map(node_utils.transfer_coinbase_tx_to_normal_tx, nodes)

        for i, node in enumerate(nodes):
            node_utils.wait_until_height_reached(node, current_height + i)
            node.execute_rpc('generate', 1)

        current_height += len(nodes)
        # TODO fix 
        self._context.first_block_height = 0 # current_height

        threadpool.starmap(node_utils.wait_until_height_reached, zip(
                nodes,
                itertools.repeat(current_height)
        ))

        threadpool.map(node_utils.rm_peers_file, nodes)
        node_utils.graceful_rm(threadpool, nodes)

    def _start_nodes(self, threadpool):
        nodes = self._context.nodes.values()

        threadpool.map(node_utils.start_node, nodes)
        threadpool.starmap(node_utils.check_startup_node, zip(
            nodes,
            itertools.repeat(self._context.first_block_height)
        ))

        threadpool.starmap(node_utils.add_latency, zip(
            self._context.nodes.values(),
            itertools.repeat(self._context.zone.zones)
        ))

        logging.info('All nodes for the simulation are started')
        utils.sleep(1)


def _remove_old_containers_if_exists():
    containers = bash.check_output(dockercmd.ps_containers())
    if len(containers) > 0:
        bash.check_output(dockercmd.remove_all_containers(), lvl=logging.DEBUG)
        logging.info('Old containers removed')


def _calc_number_of_tx_chains(txs_per_tick, blocks_per_tick, number_of_nodes):
    txs_per_block = txs_per_tick / blocks_per_tick
    txs_per_block_per_node = txs_per_block / number_of_nodes

    # 10 times + 3 chains in reserve
    needed_tx_chains = (txs_per_block_per_node / config.max_in_mempool_ancestors) * 10 + 3

    return math.ceil(needed_tx_chains)


def _recreate_network():
    exit_code = bash.call_silent(dockercmd.inspect_network())
    if exit_code == 0:
        bash.check_output(dockercmd.rm_network())
    bash.check_output(dockercmd.create_network())
    logging.info('Docker network {} created'.format(config.network_name))
    utils.sleep(1)

"""
#AppendixA

```
18-06-05 12:52:45.287000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 96.00000000
2018-06-05 12:52:45.290000 [MainProcess-Thread-3    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 1.00000000
2018-06-05 12:52:45.293000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 596.00000000
2018-06-05 12:52:45.293000 [MainProcess-Thread-3    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = -499.00000000
2018-06-05 12:52:45.294000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 96.00000000
2018-06-05 12:52:45.302000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 596.00000000
2018-06-05 12:52:45.303000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 96.00000000
2018-06-05 12:52:45.308000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 596.00000000
2018-06-05 12:52:45.308000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 96.00000000
2018-06-05 12:52:45.314000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 596.00000000
2018-06-05 12:52:45.314000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 96.00000000
2018-06-05 12:52:45.320000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 596.00000000
2018-06-05 12:52:45.320000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 96.00000000
2018-06-05 12:52:45.326000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 596.00000000
2018-06-05 12:52:45.327000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 96.00000000
2018-06-05 12:52:45.343000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 596.00000000
2018-06-05 12:52:45.344000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 96.00000000
2018-06-05 12:52:45.349000 [MainProcess-Thread-5    ] [INFO ]  Transferred all coinbase-tx to normal tx for node=node-2.5
2018-06-05 12:52:45.472000 [MainProcess-Thread-1    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 0E-8
2018-06-05 12:52:45.472000 [MainProcess-Thread-1    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = -500.00000000
2018-06-05 12:52:45.503000 [MainProcess-Thread-4    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 0E-8
2018-06-05 12:52:45.503000 [MainProcess-Thread-4    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = -500.00000000
2018-06-05 12:52:45.509000 [MainProcess-Thread-2    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 0E-8
2018-06-05 12:52:45.509000 [MainProcess-Thread-2    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = -500.00000000
2018-06-05 12:52:45.638000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = 298.00000000
2018-06-05 12:52:45.638000 [MainProcess-Thread-5    ] [INFO ]  transfer_coinbase_to_normal_tx tx_chain.amount = -202.00000000
```
"""