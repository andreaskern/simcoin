# copy network.csv and ticks.csv from ./code/handcrafted

set -e

LATENCY=$1

pushd code 

python3.6 simcoin.py nodes \
    --group-a 1 .5 $LATENCY simcoin/bitcoin:v15.0.1 \
	--group-b 1 .5 $LATENCY simcoin/bitcoin:v15.0.1

python3.6 simcoin.py simulate \
    --tick-duration=0.5

popd 

echo $(make getForks),$LATENCY,$(date) >> forks 
