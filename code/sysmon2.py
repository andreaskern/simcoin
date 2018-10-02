import time
import logging
from util import bash
import re
from threading import Thread, Event
from multiprocessing import Process
import math
import config
import csv

PRIORITY = 1

class Sysmon(Thread):
    mem_filename = config.postprocessing_dir + 'memory.csv'
    cpu_filename = config.postprocessing_dir + 'cpu_time.csv'

    mem_csv_header = [ 'timestamp'
                     , 'total'
                     , 'available'
                     , 'tag'
                     ]
    cpu_csv_header = [ 'timestamp'
                     , 'user'
                     , 'nice'
                     , 'system'
                     , 'idle'
                     , 'tag'
                     ]

    @property
    def mem(self):
        memory = bash.check_output_without_log('cat /proc/meminfo | head -3')
        memory_matched = re.match('MemTotal:\s+([0-9]+)\s+kB\n.*\nMemAvailable:\s+([0-9]+)\s+kB', memory)
        return [ time.time()
               , memory_matched.group(1)
               , memory_matched.group(2)
               , "run_10"
               ]

    @property
    def cpu(self):
        cpu_time = bash.check_output_without_log('cat /proc/stat | head -1')
        cpu_matched = re.match('cpu\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)', cpu_time)
        return [ time.time()
               , cpu_matched.group(1)
               , cpu_matched.group(2)
               , cpu_matched.group(3)
               , cpu_matched.group(4)
               , "run_10"
               ]
         

    def __init__(self, tick_duration, amount_of_ticks):
        Thread.__init__(self, target=self.run, name = "Sysmon")
        self.frequency = Sysmon.calculate_frequency( tick_duration , amount_of_ticks , config.amount_of_system_snapshots)
        self.daemon = True
        self._exit = Event()

    def run(self):
        logging.info(f'Starting system monitor with frequency={self.frequency}s')

        print(f'{config.amount_of_system_snapshots}')

        print(f'{self.frequency}')

        with open(self.cpu_filename,'w+') as fcpu, open(self.mem_filename,'w+') as fmem:
            mem_writer = csv.writer(fmem)
            cpu_writer = csv.writer(fcpu)

            print(f'{self.cpu_csv_header}')

            cpu_writer.writerow(self.cpu_csv_header)
            mem_writer.writerow(self.mem_csv_header)

            cpu_writer.writerow(self.cpu)
            mem_writer.writerow(self.mem)

            while not self._exit.wait(timeout=self.frequency): # mainloop
                # TODO why does it not write to files
                # TODO impelement new Thread/event handlind
                logging.info(f'loop {self._exit.isSet()} {self.cpu} {self.mem}' )

                cpu_writer.writerow(self.cpu)
                mem_writer.writerow(self.mem)

                # time.sleep(self.frequency)

        logging.info('Stopped System monitor')

    @staticmethod
    def calculate_frequency(tick_duration, amount_of_ticks, amount_of_system_snapshots):
        frequency = math.ceil(tick_duration * amount_of_ticks / amount_of_system_snapshots)
        logging.info(
            f'With tick_duration={tick_duration}, amount_of_ticks={amount_of_ticks} and '
            f'amount_of_system_snapshots={amount_of_system_snapshots} '
            f'the system monitor needs to take every {frequency}s a snapshot '
        )
        return frequency

    def exit(self):
        self._exit.set()
        time.sleep(0.1)
        self._exit.set()
        # self.terminate()

if __name__ == "__main__":
    event = Event()
    sysmon = Sysmon(2,10)
    sysmon.start()
    time.sleep(3)
    sysmon.exit()
    # sysmon.terminate()