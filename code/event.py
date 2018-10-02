import config
import logging
import time
import utils
from bitcoin.rpc import JSONRPCError
import math
from context import Context
from multiprocessing import Pool
import subprocess
import stopit

def check_output_without_log(cmd: str="echo NOP") -> str:
    if cmd is None:
        return ""
    # cmds = cmd.split(" ")
    logging.info("runner executing: " + cmd)
    output = subprocess.check_output(cmd, shell=True, executable='/bin/bash')
    encoded_output = output.decode('utf-8').rstrip()
    return encoded_output


class Event:

    def __init__(self, context: Context) -> None:
        self._context = context
        self._txs_count = self._blocks_count = 0

    @stopit.threading_timeoutable(default='not finished')
    def execute(self):
        try:
            utils.check_for_file(config.ticks_csv)
            with open(config.ticks_csv, 'r') as file:
                logging.info("Runner.Event.execute ticks_csv openend, starting pool")

                with Pool(2) as pool:
                    logging.info("Runner.Event.execute Pool started")

                    start_time = time.time()
                    for i, line in enumerate(file):
                        logging.info(f'Line {i} executing')
                        actual_start = time.time()
                        planned_start = start_time + i * self._context.args.tick_duration

                        self._txs_count = self._blocks_count = 0

                        if line:
                            # logging.exception(line)
                            cmds = line.rstrip().split(',')
                            if cmds == ['']:
                                continue

                            cmd_list_string = list(map(self._execute_cmd_string,list(cmds)))

                            cmd_list_string = list(map(lambda x: x.rstrip(),cmd_list_string))
                            
                            # print(pool.map(check_output_without_log,cmd_list_string))
                            for result in pool.imap_unordered(check_output_without_log,cmd_list_string):
                                logging.info(result)

                            # cmd_list = list(cmds)
                            # pool.map(shell_exec(self._execute_cmd(_x_), cmd_list,1)
                            # pool.map(self._execute_cmd, cmd_list,1)
                            # pool.close()
                            # for cmd in cmds:
                            #     self._execute_cmd_string(cmd)

                        planned_start_next_tick = start_time + (i + 1) * self._context.args.tick_duration
                        current_time = time.time()
                        duration = current_time - actual_start
                        logging.info('Tick={} with planned_start={}, actual_start={} and duration={:F},'
                                    ' created txs={} and blocks={}'
                                    .format(i, planned_start, actual_start, duration,
                                            self._txs_count, self._blocks_count))

                        if current_time < planned_start_next_tick:
                            difference = planned_start_next_tick - current_time
                            logging.info('Sleep {} seconds for next tick={}'.format(difference, i))
                            utils.sleep(difference)
                        else:  # tick took longer than planned
                            raise Exception("Tick Timeout. A Tick took longer than planned.")
                    # pool.close() # tell workers to stop
                    # pool.join()  # wait for them to stop
        except Exception:
            logging.exception('Simulation could not execute all events because of an exception')

    def _execute_cmd(self, cmd):
        cmd_parts = cmd.split(' ')
        
        self._context.get_node(cmd_parts[1]).exec_event_cmd(cmd_parts[0])

    def _execute_cmd_string(self, cmd):
        if len(cmd) == 0:
            return

        if cmd_parts[0] == 'tx':
            node = self._context.nodes[cmd_parts[1]]
            try:
                node.generate_tx()
            except JSONRPCError:
                logging.exception('Could not generate tx for node={}'.format(node.name))
            self._txs_count += 1
        elif cmd_parts[0] == 'block':
            node = self._context.nodes[cmd_parts[1]]
            try:
                node.generate_blocks()
            except JSONRPCError:
                logging.exception('Could not generate block for node={}'.format(node.name))
            self._blocks_count += 1
        elif len(cmd) == 0:
            pass
        else:
            raise SimulationException('Unknown cmd={} in {}-file'.format(cmd_parts[0], config.ticks_csv))


def _calc_analyze_skip_ticks(blocks_per_tick, tx_per_tick):
    return max([1, math.ceil(1/blocks_per_tick), math.ceil(1/tx_per_tick)])


class SimulationException(Exception):
    pass

if __name__ == "__main__":
    print("No tests")