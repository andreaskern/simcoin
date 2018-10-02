#!/usr/bin/env sh
# set -e
##set target to ?? (n+1)-times a single docker exec

# setup conatiner
docker run --rm -dt --name parallel_test_1 ubuntu top
docker exec parallel_test_1 apt update
docker exec parallel_test_1 apt install --yes bc

# calculate how long it will take to dispatch every docker call

times=10

start=$(date +%s.%N)
docker exec parallel_test_1 bash -c "echo hello world"
end=$(date +%s.%N)

## how long did this single run take
dif=$(echo "$end - $start" | bc)

## add 10%
dif=$(echo "$dif * 1.1" | bc)

## multiple by the times we want to execute docker exec
dif=$(echo "$dif * $times" | bc)

## get target time 
target=$(date -d "+0$dif seconds" +%s.%N) ;

target=$(date -d "+3 seconds" +%s.%N) ;
echo "target = $target" ; \
pexec \
        --parameters a b c d a1 a2 a3 a4 b1 b2  \
        -e x \
        -o - \
        --shell /bin/bash \
        -- /usr/bin/docker exec parallel_test_2  bash -c "target=$target; current=\$(date +%s.%N); nap=0\$(echo \"\$target - \$current\" | bc); echo \"nap=\$nap\"; sleep \$nap; sleep 0.066; now=\$(date +%s.%N); time=\$(echo \"\$now - \$target\" | bc); echo \"time=0\$time\""

#         -- /usr/bin/docker exec -t parallel_test_1  bash -c "echo \$(time sleep 1)"

### FOOO
gcc ./abssleep.c
pushd ../..; make push; popd
docker cp ./a.out parallel_test_2:/
pexec \
        --parameters a b c d a1 a2 a3 a4 b1 b2  \
        -e x \
        -o - \
        --shell /bin/bash \
        -- /usr/bin/docker exec parallel_test_2 ./a.out `date -d "+2 seconds" +"%s"`

### FOOO END

docker stop parallel_test_1

""" it works!
target = 1531764679.257119895
nap=01.404355936
nap=01.295191452
nap=01.196747949
nap=01.073302748
nap=0.953975562
nap=0.833640291
nap=0.717037041
nap=0.603612027
nap=0.509164308
nap=0.390726089
time=0.009261389
time=0.010152357
time=0.009278042
time=0.010028705
time=0.013723734
time=0.010639523
time=0.014864249
time=0.010196352
time=0.011965062
time=0.019110421
parallel_test_1
"""

## docker abssleep 2018-07-27

gcc ./abssleep.c
pushd ../..; make push; popd
docker cp ./a.out parallel_test_2:/
pexec \
        --parameters a b c d a1 a2 a3 a4 b1 b2  \
        -e x \
        -o - \
        --shell /bin/bash \
        -- /usr/bin/docker exec parallel_test_2 ./a.out `date -d "+2 seconds" +"%s"`
