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
target=$(date -d "+0$dif seconds" +%s.%N)
echo "target = $target"


docker exec parallel_test_1  bash -c "target=$target; current=$(date +%s.%N); nap=0\$(echo \"\$target - \$current\" | bc); echo \"nap=\$nap\"; sleep \$nap; now=\$(date +%s.%N); time=\$(echo \"\$now - \$target\" |bc); echo \"time=0\$time\""


docker stop parallel_test_1
