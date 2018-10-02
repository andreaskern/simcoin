#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from simulationfiles import nodes_config
from simulationfiles import ticks_config
from simulationfiles import network_config
import sys
import argparse
import simulation_cmd
from postprocessing import _create_report
import config
import os
import bitcoin
import utils
import multirun_cmd
import logging
from info import Info



def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--verbose'
                        , action="store_true"
                        , help='Verbose log.'
                        )

    parser.add_argument('--tag'
                        , default='run'
                        , help='Tag that will be added to every csv file.'
                        )

    args = parser.parse_known_args(sys.argv[2:])[0]
    utils.update_args(args)

    return args


def main():
    def run (): 
        nodes_config.create(unknown_arguments=True)
        ticks_config.create(unknown_arguments=True)
        network_config.create(unknown_arguments=True)
        simulation_cmd.run(unknown_arguments=True)

    commands = {
        'nodes':        nodes_config.create,
        'network':      network_config.create,
        'ticks':        ticks_config.create,
        'simulate':     simulation_cmd.run,
        'report'  :     _create_report,
        'run':          run,
        'multi-run':    multirun_cmd.run,
        # TODO create report
    }

    cmd_parser = argparse.ArgumentParser(
        description='Simcoin a cryptocurrency simulator.',
        usage=f'''<command> [<args>]

        The commands are:
        nodes       creates the {config.nodes_csv_file_name} for a simulation
        network     creates the {config.network_csv_file_name} for a simulation
        ticks       creates the {config.ticks_csv_file_name} for a simulation
        simulate    executes a simulation based on the {config.nodes_csv_file_name}, {config.network_csv_file_name} and {config.ticks_csv_file_name}
        report      recreate the report of the last run
        run         runs all above commands
        multi-run   run the simulation multiple times
        '''
    )
    
    cmd_parser.add_argument('command', help='Subcommand to run')

    # parse_args defaults to [1:] for args, but you need to
    # exclude the rest of the args too, or validation will fail
    args = cmd_parser.parse_args(sys.argv[1:2])
    command = args.command
    if command not in commands:
        print('Unrecognized command')
        cmd_parser.print_help()
        exit(1)

    if not os.path.exists(config.data_dir):
        os.makedirs(config.data_dir)

    bitcoin.SelectParams('regtest')

    args = _parse_args()

    utils.config_logger(args.verbose)

    logging.info(f"Arguments called with: {sys.argv}")
    logging.info(f"Parsed arguments in simcoin.py: {args}")
    logging.info(f'Executing command={command}')

    # use dispatch pattern to invoke method with same name
    commands[command]()


if __name__ == '__main__':
    main()
