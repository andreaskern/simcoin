import sched
import time
from time import sleep
import logging
import bash
import re
from threading import Thread
from multiprocessing import Process
import math
import config

PRIORITY = 1


class CpuTimeSnapshot:
    __slots__ = ['_timestamp', '_user', '_nice', '_system', '_idle']
    file_name = 'cpu_time.csv'
    csv_header = ['timestamp', 'user', 'nice', 'system', 'idle']

    def __init__(self, timestamp, user, nice, system, idle):
        self._timestamp = timestamp
        self._user = user
        self._nice = nice
        self._system = system
        self._idle = idle

    @classmethod
    def from_bash(cls, cpu_time):
        cpu_matched = re.match('cpu\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)', cpu_time)
        snapshot = cls(time.time(), cpu_matched.group(1), cpu_matched.group(2), cpu_matched.group(3), cpu_matched.group(4))
        return snapshot

    def vars_to_array(self):
        return [self._timestamp, self._user, self._nice, self._system, self._idle]


class MemorySnapshot:
    __slots__ = ['_timestamp', '_total', '_available']

    file_name = 'memory.csv'
    csv_header = ['timestamp', 'total', 'available']

    def __init__(self, timestamp, total, available):
        self._timestamp = timestamp
        self._total = total
        self._available = available

    @classmethod
    def from_bash(cls, memory):
        memory_matched = re.match('MemTotal:\s+([0-9]+)\s+kB\n.*\nMemAvailable:\s+([0-9]+)\s+kB', memory)
        snapshot = cls(time.time(), memory_matched.group(1), memory_matched.group(2))
        return snapshot

    def vars_to_array(self):
        return [self._timestamp, self._total, self._available]


class Sysmon(Process):

    def __init__(self, tick_duration, amount_of_ticks, q_cpu_time, q_memory, writer):
        Process.__init__(self, name = "Sysmon")

        self.frequency = _calculate_frequency(tick_duration, amount_of_ticks)

        self.daemon = True
        self.q_cpu_time = q_cpu_time
        self.q_memory = q_memory
        self._writer = writer

    def run(self):
        logging.info('Starting system monitor with frequency={}s'.format(str(self.frequency)))
        # scheduler = sched.scheduler(time.time, time.sleep)
        # next_execution = time.time()



        self.write_headers()

        # TODO fix sysmon
        # while True:
        logging.info("loopdy-do")
        self._collect(self.q_cpu_time, self.q_memory)
        sleep(self.frequency)
        # scheduler.enterabs(next_execution, PRIORITY, _collect, (q_cpu_time, q_memory,))
        # scheduler.run()
        # next_execution += frequency


        logging.info('Stopped System monitor')

    def _collect(self, q_cpu_time, q_memory):
        cpu_time = bash.check_output('cat /proc/stat | head -1')
        memory = bash.check_output('cat /proc/meminfo | head -3')
        # q_cpu_time.put(CpuTimeSnapshot.from_bash(cpu_time))
        # q_memory.put(MemorySnapshot.from_bash(memory))

        self.appedn_csv(
            CpuTimeSnapshot.from_bash(cpu_time), 
            MemorySnapshot.from_bash(memory)
            )

        logging.info('Collected cpu_time and memory usage')

    def write_headers(self):
        self._writer.write_header_csv(
            MemorySnapshot.file_name,
            MemorySnapshot.csv_header
            )

        self._writer.write_header_csv(
            CpuTimeSnapshot.file_name,
            CpuTimeSnapshot.csv_header
            )

    def appedn_csv(self,cpu_time, memory):
        self._writer.append_csv(
            CpuTimeSnapshot.file_name,
            [cpu_time]
        )
        self._writer.append_csv(
            MemorySnapshot.file_name,
            [memory]
        )


    def _persist_system_snapshots(self):
        cpu_times = list(self.q_cpu_time.queue)
        memory = list(self.q_memory.queue)

        self._writer.write_csv(
            CpuTimeSnapshot.file_name,
            CpuTimeSnapshot.csv_header,
            cpu_times,
        )
        self._writer.write_csv(
            MemorySnapshot.file_name,
            MemorySnapshot.csv_header,
            memory,
        )
        logging.info('Persisted {} CPU time and {} memory snapshots'.format(len(cpu_times), len(memory)))



def _calculate_frequency(tick_duration, amount_of_ticks):
    frequency = math.ceil(tick_duration * amount_of_ticks / config.amount_of_system_snapshots)
    logging.info('With tick_duration={}, amount_of_ticks={} and '
                 'amount_of_system_snapshots={} '
                 ' the system monitor needs to take every {}s a snapshot'
                 .format(tick_duration, amount_of_ticks, config.amount_of_system_snapshots, frequency))
    return frequency