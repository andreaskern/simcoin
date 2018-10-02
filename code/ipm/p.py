import time
import bitcoin

import fire

from bitcoin.rpc import Proxy, RawProxy
import os
import subprocess

import logging
logger = logging.getLogger(__name__)


class Scheduler2():
    acceptable_error = 0.015 # the wake up from sleep can be late up to 15ms

    @staticmethod
    def now():
        return time.time()


    def __init__(self, start_time):
        self.ts = start_time # in seconds
        self.log = [("rtime","ttime","offset","purpose")]

    def __del__(self):
        print('\n'.join(map(str,self.log)))

    def wait(self):
        """ wait for start_time """
        self.log.append((self.now(),self.ts,self.ts - self.now(),"wait"))
        self.save_sleep(0)
        self.log.append((self.now(),self.ts,self.ts - self.now(),"wait"))


    def save_sleep(self, delta): # in seconds
        self.ts += delta
        if delta < 0:
            raise Exception(f"delta is negative {delta} ")
        
        if self.ts < self.now():
            diff = self.now()-self.ts
            raise Exception(f"Last Operation took to long, sleep target was missed by {diff}")        
            
        
        #time.sleep(self.ts - self.now())
        target = self.ts - self.now()
        subprocess.run(f"sleep {target}".split(" "), stdout=subprocess.PIPE)
        
        self.log.append((self.now(),self.ts,self.ts - self.now(),"sleep"))

        if self.now() > self.ts + self.acceptable_error :
            err = self.now() - (self.ts + self.acceptable_error)
            raise Exception(f"Did not wake up fast enough, missing {err} seconds")

class Process:
    """ TODO startsignal """

    #def __init__(self):
        # DONE run bitcoind as subprocess
        # TODO do something with bitcoind's output, e.g. input/output tape emulation
        # TODO run "strategy"
        # self.input_i*d_tape = file.read("/id")
    
    def __del__(self):
        # TODO stop bitcoind
        return True
    
    def run(self, id, nodes, start_at_timestamp):
        # all times are in seconds
        s = Scheduler2(int(start_at_timestamp))
        blocktime = 0.2 # seconds

        self.set_network_delay()

        s.wait()

        
        self.startd()
        self.rpc    = Proxy(service_url="http://admin:admin@localhost:18332")
        self.rpc_a  = RawProxy(service_url="http://admin:admin@localhost:18332")

        generateBlock = lambda: self.rpc.generate(1)
        getChainTips =  lambda: self.rpc_a.getchaintips()


        s.save_sleep(15)

        logger.error(f"[{id}] setup phase complete ")

        # generate first round blocks
        s.save_sleep(id * blocktime)
        generateBlock()
        logger.error(f"[{id}] generated initial blocks")
        s.save_sleep((nodes - id) * blocktime + 0.5)


        # generate doublespends, synchronous block creation
        for _ in range(10):
            if id % 2 == 1:
                s.save_sleep(blocktime + 0.2)
                generateBlock()
                s.save_sleep(0.2)
                logger.error(f"[{id}] Tick")
            else:
                s.save_sleep(0.2)
                generateBlock()
                logger.error(f"[{id}] Tock")
                s.save_sleep(blocktime + 0.2)

        # generate last round of blocks

        logger.error(f"[{id}] Last round")

        s.save_sleep(id * blocktime)
        generateBlock()
        s.save_sleep((nodes - id) * blocktime + 0.2)

        logger.error(f"[{id}] Done")


        # the following part uses cog as code generation tool
        # python -mpip install cogapp
        # python -mcogapp -r p.py

        # [[[cog
        # import cog
        # cog.out("print('hello')")
        # ]]]
        print('hello')

        tips = getChainTips()

        # [[[end]]]

        self.stopd()

        print(tips)
        with open("output.tape","w") as out:
            out.write(str(tips))

        exit()

    daemon = '/usr/local/bin/bitcoind'
    args = {
        'regtest':            '-regtest',
        'datadir':            '-datadir=/tmp',

        # disable security checks for better performance
        'whitelist': '-whitelist=240.0.0.0/4',

        # log all events relevant for parsing
        'debug':              '-debug=cmpctblock -debug=net -debug=mempool',
        'logips':             '-logips',
        'logtimemicros':      '-logtimemicros',


        # activate listen even though explicit -connect will be set
        'connect':            '-connect=240.0.0.2', #bootstrap
        'listen':             '-listen=1',
        'listenonion':        '-listenonion=0',
        'onlynet':            '-onlynet=ipv4',
        'dnsseed':            '-dnsseed=0',

        'reindex':            '-reindex',
        'checkmempool':       '-checkmempool=0',
        'keypool':            '-keypool=1',

        # RPC configuration
        'rpcuser':            '-rpcuser=admin',
        'rpcpassword':        '-rpcpassword=admin',
        'rpcallowip':         '-rpcallowip=1.1.1.1/0.0.0.0',
        'rpcservertimeout':   '-rpcservertimeout=3600',
        'rpcport':            '-rpcport=18332'
    }

    def startd(self):
        with open("output_daemon.log","wb") as out:
            self.daemon = subprocess.Popen([self.daemon] + list(self.args.values()),stdout=out)

    def stopd(self):
        self.daemon.terminate()

    def set_network_delay(self):
        cmds = [
            'tc qdisc add '    # Traffic_Control Queue_DISCipline add
            ' dev eth0 '       # DEVice eth0
            ' root '           # ROOT_egress_outbound_location
            ' netem delay 10700ms '
        ]

        subprocess.Popen(cmds[0].split(' '))

    def rm_peers(self, node):
        return "" # TODO dockercmd.exec_cmd(node, 'rm -f {}/regtest/peers.dat'.format(config.bitcoin_data_dir))

    def show_command(self):
        print(self.daemon + ' '.join(self.args.values()))

    def clean(self):
        print("nop")


if __name__ == '__main__':
  fire.Fire(Process)



# import numpy
import itertools
    # scheduler.add(interval_in_seconds=10*60,distribution="poisson",cmd="generateblock 1 true")
    # scheduler.add("every ten 10 minutes on average Poisson distributed trigger block found")
    # scheduler.add("every 30 minutes add 1 % of nodes")
    # scheduler.add("every `1/2.5` seconds create transaction")
    # scheduler.onFinish(lambda: print("hello world"))
    # schedule = scheduler.getSchedule()


class Scheduler(list):

    def __init__(self):
        list.__init__(self)

    def append(self, item):
        self.append(item)

    def merge(self, delay_queue):
        self.extend(delay_queue)
        self.sort()

    def addblocks(self,count,cmd):
        numpy.random.seed(0)
        s = numpy.random.exponential(scale=15.0, size=count, ) # TODO set to 600
        ss = itertools.accumulate(s)
        f = itertools.cycle( cmd )
        fs = zip(ss,f)
        self.merge(fs)

    def addtransactions(self, count, cmd):
        tps = 1  # transactions per second TODO set to 2.5
        time = numpy.arange(1.0, count,1.0/tps)
        # times = itertools.accumulate(time)
        f = itertools.cycle(cmd)
        plan = zip(time, f)
        self.merge(plan)

    def bash_commands(self):
        times, cmds = zip(*self)
        prev_times = [0] + list(times)
        time_tuples = list(zip(prev_times, times))
        deltas = list(map(lambda x: x[1]-x[0], time_tuples))
        sleeps = list(map((lambda t : " sleep {:5.5f} ; {} \n".format(t[0],t[1])),zip(deltas,cmds)))
        plan = "echo Begin of Scheduled commands\n {}".format(" ".join(sleeps))
        return plan
