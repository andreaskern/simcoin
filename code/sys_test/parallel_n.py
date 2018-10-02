import time
import os
import itertools
from bitcoin.rpc import JSONRPCError
from multiprocessing import Pool as Processes
from multiprocessing.dummy import Pool as Threads
import subprocess

"""
# How fast can the host system execute commands?

This factor depends mostly on number of cpus/cores/threads.
There is a tradeoff between parallelism and latency.
With an increasing number of actions executing, the overall time increases.


"""

def bash(cmd):
    subprocess.check_output(cmd, shell=True, executable='/bin/bash')
    return time.time()

def shell(cmd):
    subprocess.check_output(cmd, shell=True, executable='/bin/sh')
    return time.time()

def unchecked(cmd):
    subprocess.run(cmd.split(" "), stdout=subprocess.PIPE)
    return time.time()


class test_containers():

    @property
    def conatiners(self):
        ## TODO return list(range(self.n)).map(lambda index: self.prefix + str(index))

    def __init__(self, n):
        self.prefix="parallel_test_"
        self.n=n
        return None

    def __enter__(self):
        for i in range(self.n):
            subprocess.check_output(f"docker run -dt --name={self.prefix+str(i)} ubuntu top", shell=True, executable='/bin/sh')
        return self
    
    def __exit__(self ,type, value, traceback):
        for i in range(self.n):
            subprocess.check_output(f"docker stop {self.prefix+str(i)} ubuntu top", shell=True, executable='/bin/sh')
        for i in range(self.n):
            subprocess.check_output(f"docker rm  {self.prefix+str(i)} ubuntu top", shell=True, executable='/bin/sh')


def execute(parallelism=8,cmd_list_string = ['date +"%T.%6N"']*100):


    def do_something(prefix,pool,f):
        minT = 10  # ~10s as upper bound
        maxT = 0   # ~0s as lower bound
        for i in range(15):
            start = time.time()
            
            for result in pool.map(f ,cmd_list_string):
                duration = result - start
                minT = min(minT,duration)
                maxT = max(maxT,duration)
                # print(result)

            duration = time.time() - start
            # print(f'---{duration}')
        print(f'={prefix}=(max={maxT:.8f},min={minT:.8f},dif={maxT-minT:.8f})===')

    with Processes(parallelism) as pool:
        do_something("pb",pool,bash)
        do_something("ps",pool,shell)
        do_something("pu",pool,unchecked)

    with Threads(parallelism) as pool:
        do_something("tb",pool,bash)
        do_something("ts",pool,shell)
        do_something("tu",pool,unchecked)

def p_execute(parallelism=8,cmd_list_string = ['date +"%T.%6N"']*100):

    def do_something(prefix):
        minT = 10  # ~10s as upper bound
        maxT = 0   # ~0s as lower bound
        for i in range(15):
            start = time.time()
            
            out = pexec()

            duration = time.time() - start
            print(f'---{duration}')

            for result in out.splitlines():
                # print(f'---XX{result}')
                duration = float(result) - start
                minT = min(minT,duration)
                maxT = max(maxT,duration)
                print(f'---DD{duration}')

        print(f'={prefix}=(max={maxT:.8f},min={minT:.8f},dif={maxT-minT:.8f})===')

    do_something("pexec")

def commandbuilder():
    shell                 = ['bash','sh','eval']
    virtualization        = ['docker',''] # empty means no virt used
    pool_type             = [Threads, Processes]
    map_type              = [lambda x: x.map, lambda x: x.imap, lambda x: x.imap_unordered]
    parallel_executions   = [int(os.cpu_count()/2),os.cpu_count(), os.cpu_count()*2, os.cpu_count()*4]

    combos = itertools.product(shell, virtualization, pool_type, )
    cmds   = list(map(' '.join,list(map(lambda x: list(map(str,x)), combos))))



def sleep_until():
    script = '''

    target=$(date -d "+10 seconds" +%s.%N$)
    current=$(date %s.%N)
    diff=$(echo "$target - $current"|bc)
    cmd='target=$target`; echo $target; current=$(date +%s.%N); echo $(echo "$target - $current"|bc); date +%s.%N'
    docker exec test sh -c 'current=$(date +%s.%N); sleep $(echo "$target - $current"|bc); date +%s.%N'
    "$(`date -d '01/01/2010 12:00' +%s` - `date +%s.%N`|bc)"

    target=$(date -d "+10 seconds" +%s.%N); echo $target
    docker exec test  bash -c "target=$target; echo \$target; current=$(date +%s.%N); echo \$(echo \"\$target - \$current\"|bc); date +%s.%N" &

    # don't forget to `apt install --yes bc`

    target=$(date -d "+10 seconds" +%s.%N); echo $target
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    docker exec test bash -c "target=$target; current=$(date +%s.%N); sleep \$(echo \"\$target - \$current\"|bc); date +%s.%N" &
    echo "started"

1531335018.495008018
1531335018.604680861
1531335018.724583604
1531335018.826303812
1531335018.945360960
1531335019.085612546
1531335019.168397022
1531335019.317953719
1531335019.405185865
1531335019.515091101
1531335019.615134039
1531335019.752214761
1531335019.876336913
1531335019.965527283
1531335020.074935032
1531335020.212300409
1531335020.303367307
1531335020.425141550


    target=$(date -d "+10 seconds" +%s.%N); echo $target
    fun () { current=$(date +%s.%N); sleep $(echo "$target - $current"|bc); date +%s.%N; }
    fun &
    fun &
    fun &
    fun &
    fun &
    fun &
    fun &
    fun &
    fun &
    fun &
    fun &
    fun &
    fun &
    fun &
    fun &
    fun &

1531335356.185475462
1531335356.185303124
1531335356.187134165
1531335356.187099859
1531335356.187645542
1531335356.188367287
1531335356.187975669
1531335356.188726765
1531335356.189567642
1531335356.190568708
1531335356.191160860
1531335356.191537247
1531335356.192084766
1531335356.193364190
1531335356.194488443
1531335356.197890571


echo $(sleep 1 ; date +%s.%N) & echo $(sleep 1; date +%s.%N) & echo $(sleep 1; date +%s.%N) &

1531335523.582223860
1531335523.584996749
1531335523.586194647


    echo "started"
    '''

""" Documentation
running the 100 date commands with 100 pool workers in parallel in a single docker container yields following results.
max/min gives the time between start and the value the thread returned.
max/min is given in seconds


local (thinkpad x240) results (Intel(R) Core(TM) i5-4200U CPU @ 1.60GHz) (2c/4t) 4589.58 bogomips / 8gb ram
)

    ==(max=6.456315040588379,min=0.19557499885559082)===
    ==(max=6.833608150482178,min=0.14405417442321777)===


server (QEMU,16cores, Intel, 2.4Ghz) # guess is Xeon(R) CPU E5-2630 v3 (8c/16t; max 2 CPUs) 4799.99 bogomips / 55gb ram

    ==(max=11.573967456817627,min=5.797327518463135)===
    ==(max=11.572788715362549,min=4.089322090148926)=== # after removing munin/apache2
    ==(max=11.464806079864502,min=4.169759035110474)===


## switch multiprocessing to multiprocessing.dummy to use threading

new results

    server: ==(max=11.690826654434204,min=2.1545698642730713)===
    local:  ==(max=7.100238084793091,min=0.8446128368377686)===

switching back to without dummy

    server: ==(max=11.742754697799683,min=3.772214651107788)===
    local:  ==(max=6.5073018074035645,min=0.7535111904144287)===

"""

"""

# improved results

local:
    [Running] python3.6 "/home/kern/ak/bac/code/sys_test/parallel.py"
    n=2
    =pb=(max=0.22272182,min=0.11429572,dif=0.10842609)===
    =ps=(max=0.15840840,min=0.11331534,dif=0.04509306)===
    =pu=(max=0.25522184,min=0.11797595,dif=0.13724589)===
    =tb=(max=0.20380974,min=0.11656427,dif=0.08724546)===
    =ts=(max=0.14909506,min=0.11422372,dif=0.03487134)===
    =tu=(max=0.15027809,min=0.11372042,dif=0.03655767)===
    n=4
    =pb=(max=0.38268065,min=0.23483324,dif=0.14784741)===
    =ps=(max=0.28403616,min=0.22100854,dif=0.06302762)===
    =pu=(max=0.28389072,min=0.24490428,dif=0.03898644)===
    =tb=(max=0.30051827,min=0.23422146,dif=0.06629682)===
    =ts=(max=0.29994106,min=0.21089578,dif=0.08904529)===
    =tu=(max=0.28447151,min=0.23521948,dif=0.04925203)===
    n=8
    =pb=(max=0.57238579,min=0.48724532,dif=0.08514047)===
    =ps=(max=0.58540106,min=0.48395514,dif=0.10144591)===
    =pu=(max=0.56357121,min=0.46628404,dif=0.09728718)===
    =tb=(max=0.53821111,min=0.48298717,dif=0.05522394)===
    =ts=(max=0.55258584,min=0.49532294,dif=0.05726290)===
    =tu=(max=0.65602255,min=0.48072529,dif=0.17529726)===
    n=16
    =pb=(max=1.22615385,min=0.63361621,dif=0.59253764)===
    =ps=(max=1.06685162,min=0.96152544,dif=0.10532618)===
    =pu=(max=1.09949946,min=0.96458530,dif=0.13491416)===
    =tb=(max=1.09377956,min=0.66254258,dif=0.43123698)===
    =ts=(max=1.08000565,min=0.71138787,dif=0.36861777)===
    =tu=(max=1.16923881,min=0.78004622,dif=0.38919258)===

server:
    
    andreas@simcoin:/blockchain/kern/simcoin/code/sys_test$ python3.6 ./parallel.py 
    n=8
    =pb=(max=1.04983091,min=0.87678766,dif=0.17304325)===
    =ps=(max=1.00153303,min=0.86780024,dif=0.13373280)===
    =pu=(max=0.98966312,min=0.82180333,dif=0.16785979)===
    =tb=(max=1.00102305,min=0.86913300,dif=0.13189006)===
    =ts=(max=0.98747087,min=0.12454605,dif=0.86292481)===
    =tu=(max=0.99685907,min=0.85857534,dif=0.13828373)===
    n=16
    =pb=(max=1.99367166,min=1.77265429,dif=0.22101736)===
    =ps=(max=1.94471312,min=1.69224024,dif=0.25247288)===
    =pu=(max=1.93382454,min=1.77363992,dif=0.16018462)===
    =tb=(max=1.98978066,min=1.76150727,dif=0.22827339)===
    =ts=(max=1.92345357,min=1.77404714,dif=0.14940643)===
    =tu=(max=1.94487500,min=1.77337360,dif=0.17150140)===
    n=32
    =pb=(max=3.84190631,min=3.56040263,dif=0.28150368)===
    =ps=(max=3.81679058,min=3.56343985,dif=0.25335073)===
    =pu=(max=3.78452969,min=3.57417941,dif=0.21035028)===
    =tb=(max=3.79575372,min=3.58264208,dif=0.21311164)===
    =ts=(max=3.83207703,min=3.58581066,dif=0.24626637)===
    =tu=(max=3.80990410,min=3.14288616,dif=0.66701794)===
    n=64
    =pb=(max=7.61245418,min=4.70219278,dif=2.91026139)===
    =ps=(max=7.60093808,min=5.76981878,dif=1.83111930)===
    =pu=(max=7.55082321,min=6.40552402,dif=1.14529920)===
    =tb=(max=7.49270797,min=2.03954935,dif=5.45315862)===
    =ts=(max=7.50486422,min=2.47251487,dif=5.03234935)===
    =tu=(max=7.58262920,min=2.53459072,dif=5.04803848)===

"""


"""

parallel background sleep

echo $(sleep 1 ; date +%s.%N) & echo $(sleep 1; date +%s.%N) & echo $(sleep 1; date +%s.%N) &

echo "parallel subshell background sleep" & \
echo sh -c "$(sleep 1; date +%s.%N)" & \
echo sh -c "$(sleep 1; date +%s.%N)" & \
echo sh -c "$(sleep 1; date +%s.%N)" & \
echo sh -c "$(sleep 1; date +%s.%N)" & \
echo sh -c "$(sleep 1; date +%s.%N)" & \
echo sh -c "$(sleep 1; date +%s.%N)" & \
echo sh -c "$(sleep 1; date +%s.%N)" & \
echo sh -c "$(sleep 1; date +%s.%N)" & \
echo sh -c "$(sleep 1; date +%s.%N)" &

echo "parallel subshell background sleep" & \
 sh -c "$(sleep 1; date +%s.%N)" & \
 sh -c "$(sleep 1; date +%s.%N)" & \
 sh -c "$(sleep 1; date +%s.%N)" & \
 sh -c "$(sleep 1; date +%s.%N)" & \
 sh -c "$(sleep 1; date +%s.%N)" & \
 sh -c "$(sleep 1; date +%s.%N)" & \
 sh -c "$(sleep 1; date +%s.%N)" & \
 sh -c "$(sleep 1; date +%s.%N)" & \
 sh -c "$(sleep 1; date +%s.%N)" & \
 date +%s.%N

 ~ 1ms dispatch time

 """


"""

to monitor use `top` with `f` to filter for cpu and `u` to filter for user
`sleep` seems to be scheduled only once per cpu_thread, 

 pexec
  pexec \
    --parameters a1 a2 a3 a4 b1 b2 b3 b4 c1 c2 c3 c4 d1 d2 d3 d4 e1 e2 e3 e4 f1 f2 f3 f4 \
    -e x \
    -o - \
    --shell /bin/bash \
    --shell-command 'sleep 5; date +%s.%N'

local (x240):
    executes every ~2ms
    groups in blocks of 4 (2c/4t) with 1 second between
kern@x240:~/ak/bac$   pexec \
>     --parameters a1 a2 a3 a4 b1 b2 b3 b4 c1 c2 c3 c4 d1 d2 d3 d4 e1 e2 e3 e4 f1 f2 f3 f4 \
>     -e x \
>     -o - \
>     --shell /bin/sh \
>     --shell-command 'sleep 1; date +%s.%N'
1531732174.854332986
1531732174.856934554
1531732174.858657768
1531732174.860103920
1531732175.861315553
1531732175.864065718
1531732175.864098560
1531732175.866314345
1531732176.868085576
1531732176.870907327
1531732176.873380830
1531732176.874944071
1531732177.873667992
1531732177.879598987
1531732177.882015058
1531732177.883761427
1531732178.879579020
1531732178.887133189
1531732178.888182599
1531732178.890492827
1531732179.885904906
1531732179.893906684
1531732179.895296769
1531732179.896478791

    andreas@simcoin:~$   pexec -r a1 a2 a3 a4 b1 b2 b3 b4 c1 c2 c3 c4 d1 d2 d3 d4 e1 e2 e3 e4 f1 f2 f3 f4 -e x -o - -c \
>     'sleep 1; date +%s.%N'
1531731782.184109665
1531731782.184861179
1531731782.188011444
1531731782.189967831
1531731782.190051928
1531731782.191019101
1531731782.191354532
1531731782.191805294
1531731782.191965231
1531731782.192649293
1531731782.193265045
1531731782.194352435
1531731782.194586259
1531731782.196231832
1531731782.196390109
1531731782.197046634
1531731783.189980550
1531731783.194764345
1531731783.195960180
1531731783.197609322
1531731783.197935206
1531731783.198580308
1531731783.199837889
1531731783.200875143


"""

def pexec():


    # { with, without } docker exec
    # parse time
    # do statistics

    with test_containers(16) as t:
        # execute([f"docker exec {t.container_name} date; echo 1"]*128)
        # n = os.cpu_count()

        para1 = " a1 "
        ## =pexec=(max=0.75104666,min=0.58403230,dif=0.16701436)===

        para2 = " a1 a2 "
        ## =pexec=(max=0.82753468,min=0.58369684,dif=0.24383783)===

        para4 = " a1 a2 a3 a4 "
        ## =pexec=(max=1.04095721,min=0.57291746,dif=0.46803975)===

        para16 = " a1 a2 a3 a4 b1 b2 b3 b4 c1 c2 c3 c4 d1 d2 d3 d4 "
        ## =pexec=(max=2.39530110,min=0.57797098,dif=1.81733012)===

        para17 = " a1 a2 a3 a4 b1 b2 b3 b4 c1 c2 c3 c4 d1 d2 d3 d4 X "
        para32 = para16 * 2
        ## =pexec=(max=4.27226233,min=0.57683969,dif=3.69542265)===
        para64 = para32 * 2
        ## =pexec=(max=8.05523825,min=0.57982135,dif=7.47541690)===

        ## TODO do real parallelisation

        cmd_with_docker = f"""  pexec \
        --parameters {para16} \
        -e x \
        -o - \
        --shell /bin/bash \
        --shell-command '/usr/bin/docker exec {t.container_name_1} sh -c "sleep 1; date +%s.%N"' \
        & \
        pexec \
        --parameters {para16} \
        -e x \
        -o - \
        --shell /bin/bash \
        --shell-command '/usr/bin/docker exec {t.container_name_2} sh -c "sleep 1; date +%s.%N"' \
        & \

        """

        cmd_without_docker = f"""  pexec \
        --parameters {para16} \
        -e x \
        -o - \
        --shell /bin/bash \
        --shell-command 'sh -c "sleep 1; date +%s.%N"' \
        & \
        pexec \
        --parameters {para16} \
        -e x \
        -o - \
        --shell /bin/bash \
        --shell-command 'sh -c "sleep 1; date +%s.%N"' \
        & \

        """

        cmd = cmd_with_docker

        out = subprocess.check_output(cmd, shell=True, executable='/bin/sh')

    return out

"""
 pexec \
        --parameters a1 a2 a3 a4 b1 b2 b3 b4 c1 c2 c3 c4 d1 d2 d3 d4 \
        -e x \
        -o - \
        --shell /bin/bash \
        --shell-command '/usr/bin/docker exec ptest; date +%s.%N'
        
"""

"""

kern@x240 ~> pexec \
                     --parameters a1 a2 a3 a4 b1 b2 b3 b4 c1 c2 c3 c4 d1 d2 d3 d4 \
                     -e x \
                     -o - \
                     --shell /bin/bash \
                     --shell-command '/usr/bin/docker exec ptest sh -c "sleep 4; date +%s.%N"'
1531743604.595765589
1531743604.655058507
1531743604.846127677
1531743604.847545091
1531743608.849444118
1531743608.892165281
1531743608.967078768
1531743609.030129287
1531743612.958309015
1531743613.040217195
1531743613.119417589
1531743613.223445126
1531743617.027978543
1531743617.115493846
1531743617.191746445
1531743617.295630729

kern@x240 ~> pexec \
                     --parameters a1 a2 a3 a4 b1 b2 b3 b4 c1 c2 c3 c4 d1 d2 d3 d4 \
                     -e x \
                     -o - \
                     --shell /bin/bash \
                     --shell-command '/usr/bin/docker exec ptest sh -c " date +%s.%N"'
1531744687.518563892
1531744687.535114734
1531744687.590641477
1531744687.629597249
1531744687.717927725
1531744687.786555982
1531744687.847000835
1531744687.915471018
1531744687.999214700
1531744688.059153827
1531744688.127367612
1531744688.194522025
1531744688.282032239
1531744688.360538070
1531744688.411004978
1531744688.479603726

andreas@simcoin:~$  pexec                      --parameters a1 a2 a3 a4 b1 b2 b3 b4 c1 c2 c3 c4 d1 d2 d3 d4                      -e x                      -o -                      --shell /bin/bash                      --shell-command '/usr/bin/docker exec ptest sh -c "sleep 4; date +%s.%N"'
1531745100.664395136
1531745100.791970395
1531745100.900320671
1531745100.997031659
1531745101.127746043
1531745101.255794740
1531745101.388679943
1531745101.512942151
1531745101.632755951
1531745101.755505329
1531745101.886163585
1531745102.003898634
1531745102.126783577
1531745102.224638452
1531745102.340958878
1531745102.452087320

andreas@simcoin:~$  pexec                      --parameters a1 a2 a3 a4 b1 b2 b3 b4 c1 c2 c3 c4 d1 d2 d3 d4                      -e x                      -o -                      --shell /bin/bash                      --shell-command '/usr/bin/docker exec ptest sh -c " date +%s.%N"'
1531745166.512753255
1531745166.616697972
1531745166.761080800
1531745166.893444550
1531745167.018874894
1531745167.126915315
1531745167.259710979
1531745167.377833771
1531745167.486439424
1531745167.612121586
1531745167.715654494
1531745167.837190349
1531745167.956031440
1531745168.080077328
1531745168.198090697
1531745168.310990558

andreas@simcoin:~$ pexec                      --parameters a1 a2 a3 a4 b1 b2 b3 b4 c1 c2 c3 c4 d1 d2 d3 d4                      -e x                      -o -                      --shell /bin/bash                      --shell-command 'date +%s.%N'1531745213.431790131
1531745213.433396120
1531745213.433574714
1531745213.434387963
1531745213.435225757
1531745213.435480691
1531745213.435554861
1531745213.435786636
1531745213.436406381
1531745213.436974220
1531745213.437031967
1531745213.437939795
1531745213.438062720
1531745213.439818512
1531745213.440285393
1531745213.440292629


"""

if __name__ == "__main__":
    p_execute()
    exit(0)
    with test_container() as t:
        # execute([f"docker exec {t.container_name} date; echo 1"]*128)
        n = os.cpu_count()
        n_half = int(n/2)
        n_double = n*2
        n_quad = n*4
        print(f"n={n_half}")
        execute(parallelism=n_half,cmd_list_string = [f"/usr/bin/docker exec {t.container_name} echo 1"]*n_half)
       
        print(f"n={n}")
        execute(parallelism=n,cmd_list_string = [f"/usr/bin/docker exec {t.container_name} echo 1"]*n)
       
        print(f"n={n_double}")
        execute(parallelism=n_double,cmd_list_string = [f"/usr/bin/docker exec {t.container_name} echo 1"]*n_double)

        print(f"n={n_quad}")
        execute(parallelism=n_quad,cmd_list_string = [f"/usr/bin/docker exec {t.container_name} echo 1"]*(n_quad))

        # execute([f"  echo 1"]*64)

"""
docker run --rm -dt --name parallel_test_1 ubuntu top
docker run --rm -dt --name parallel_test_2 ubuntu top


date +%s.%N; \
pexec \
        --parameters a b c d a b c d  \
        -e x \
        -o - \
        --shell /bin/bash \
        --shell-command '/usr/bin/docker exec parallel_test_1 sh -c "sleep 1; date +%s.%N"' \
        ; date +%s.%N & \
        pexec \
        --parameters a b c d a b c d \
        -e x \
        -o - \
        --shell /bin/bash \
        --shell-command '/usr/bin/docker exec parallel_test_2 sh -c "sleep 1; date +%s.%N"' \
        ; date +%s.%N & \

"""

"""
pexec \
        --parameters parallel_test_1 parallel_test_1 parallel_test_2 parallel_test_2  \
        -e x \
        -o - \
        --shell /bin/bash \
        --shell-command '/usr/bin/docker exec $x sh -c "sleep 10; date +%s.%N"'
"""

"""

## see bash script test1.sh

"""