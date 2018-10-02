PYTHON=python3.6
USER=xxx
SERVERIP=xxx

all:
	echo "Run the following targets manually install, build-image, test, run"

demo:
	cd code; \
		$(PYTHON) simcoin.py \
			run \
				--group-a 2 .6 0 simcoin/bitcoin:v15.0.1 \
				--group-b 1 .4 0 simcoin/bitcoin:v15.0.1 \
				--amount-of-ticks 10 \
				--txs-per-tick 2 \
				--blocks-per-tick 0.7 \
				--system-snapshots-frequency 2

demo_medium:
	cd code; \
		$(PYTHON) simcoin.py \
			run \
				--group-a 2 .6 0 simcoin/bitcoin:v15.0.1 \
				--group-b 1 .4 0 simcoin/bitcoin:v15.0.1 \
				--amount-of-ticks 20 \
				--txs-per-tick 4 \
				--blocks-per-tick 0.7 \
				--system-snapshots-frequency 2

demo_single:
	cd code; \
		$(PYTHON) simcoin.py \
			run \
				--group-a 1 1 0 simcoin/bitcoin:v15.0.1 \
				--amount-of-ticks 20 \
				--txs-per-tick 4 \
				--blocks-per-tick 0.7 \
				--system-snapshots-frequency 2

multidemo:
	cd code; \
		$(PYTHON) simcoin.py \
			multi-run \
				--repeat 2 \
				--group-a 2 .6 10 simcoin/bitcoin:v15.0.1 \
				--group-b 1 .4 10 simcoin/bitcoin:v15.0.1 \
				--blocks-per-tick 0.9 \
				--amount-of-ticks 7 \
				--txs-per-tick 10 \
				--tick-duration 1 \
				--system-snapshots-frequency 1

install:
	# for kableExtra
	sudo apt install libmagick++-dev
	sudo apt install pandoc
	sudo apt install bc # for `make getForks`
	sudo apt install python3-pip # for gitlab image
	## for Ubuntu 16.04.4 LTS because python3.6 is not available in the standard repos
	# sudo add-apt-repository ppa:deadsnakes/ppa
	# sudo apt-get update
	# sudo apt-get install python3.6
	cd code; python3.6 -m pip install -r requirements.txt
	sudo R -e "update.packages(ask=FALSE, repos='https://cran.wu.ac.at')"
	sudo R -e "install.packages(c('rmarkdown','devtools','jsonlite','dplyr','anytime', 'kableExtra', 'lattice', 'reshape2'), repos='https://cran.wu.ac.at')"
	# https://stackoverflow.com/questions/20923209/problems-installing-the-devtools-package

edit-report:
	cd code; \
		cp reporter/report.Rmd ../data/last_run/postprocessing/; \
		cd ../data/last_run/postprocessing/; \
		rstudio report.Rmd; \
		# R -e library\(rmarkdown\)\;rmarkdown::render\(\"report.Rmd\",\"pdf_document\"\)\;q\(\);rm report.Rmd

ssh:
	echo "ssh -p 2222 -L 9099:localhost:9090 $(USER)@$(SERVERIP)"

getForks:
	@echo $$(cat ./data/last_run/postprocessing/forks.csv | wc -l)-1 | bc

bounds: 
	bash ./find_\ bounds.sh {(seq -s ',' 0 25 250)}

build-image:
	cd ./code/docker; \
	docker build --no-cache --tag simcoin/bitcoin:v15.0.1 .

rm-image:
	docker rmi simcoin/bitcoin:v15.0.1

cp-run:
	rm -r /tmp/run; \
	mkdir /tmp/run; \
	cp -r data/last_run/* /tmp/run/.

cp-multi:
	rm -r /tmp/run; \
	mkdir /tmp/run; \
	mkdir /tmp/run/postprocessing; \
	cp -r data/last_multi_run/* /tmp/run/postprocessing/.

.PHONY : test
test:
	cd code; \
		$(PYTHON) \
			-m unittest discover \
			-s tests

.PHONY : clean
clean:
	rm -rf data/*
	docker stop `docker ps --quiet --filter name=simcoin`

SEQ=$(shell seq 100)
SCRIPT_CLI_HOST="time for x in $(SEQ) ; do ~/bitcoin/bin/bitcoin-cli -regtest -rpcuser=admin -rpcpassword=admin  generate 1 > /dev/null; done"
SCRIPT_CLI_DCKR="time for x in $(SEQ) ; do docker exec simcoin_exp1 bitcoin-cli -regtest -rpcuser=admin -rpcpassword=admin generate 1 > /dev/null; done"
SCRIPT_NAT_HOST="time sh -c '~/bitcoin/bin/bitcoin-cli -regtest -rpcuser=admin -rpcpassword=admin generate 100 > /dev/null'"
SCRIPT_LOO_DCKR="time docker exec simcoin_exp1 sh -c 'for x in $(SEQ); do bitcoin-cli -regtest -rpcuser=admin -rpcpassword=admin generate 1 > /dev/null; done'"
SCRIPT_NAT_DCKR="time docker exec simcoin_exp1 sh -c 'bitcoin-cli -regtest -rpcuser=admin -rpcpassword=admin generate 100 > /dev/null'"

HOST_INIT="~/bitcoin/bin/bitcoind -regtest -daemon -rpcuser=admin -rpcpassword=admin ; sleep 2"
HOST_EXIT="~/bitcoin/bin/bitcoin-cli -regtest -rpcuser=admin -rpcpassword=admin stop; sleep 1"

DCKR_INIT="docker run --interactive --tty --detach --rm --name simcoin_exp1 simcoin/bitcoin:v15.0.1 bitcoind -regtest -rpcuser=admin -rpcpassword=admin; sleep 3"
DCKR_EXIT="docker rm -f simcoin_exp1"
experiment_1:
	#         | cli / looped-cli
	#---------|----------------
	# host    | 
	# docker  |
	#
	# download bitcoind on host machine // https://bitcoin.org/bin/bitcoin-core-0.16.2/bitcoin-0.16.2-x86_64-linux-gnu.tar.gz
    # extract to ~/bitcoin
	# server (local/x240)
	
	# docker -> loop 100 -> gen 1
	# 1.892s (8.631s)
	bash -c $(DCKR_INIT)
	bash -c $(SCRIPT_LOO_DCKR)
	bash -c $(DCKR_EXIT)

	# loop 100 -> docker -> gen 1
	# 15.935s (15.211s)
	bash -c $(DCKR_INIT)
	bash -c $(SCRIPT_CLI_DCKR)
	bash -c $(DCKR_EXIT)

	# loop 100 -> host -> gen 1
	# 2.608s (8.627s)
	bash -c $(HOST_INIT)
	bash -c $(SCRIPT_CLI_HOST)
	bash -c $(HOST_EXIT)

	# loop 1 -> host -> gen 100
	# 0.846s (0.301s)
	bash -c $(HOST_INIT)
	bash -c $(SCRIPT_NAT_HOST)
	bash -c $(HOST_EXIT)

	# loop 1 -> docker -> gen 100
	# 0.259s (0.163s)
	bash -c $(DCKR_INIT)
	bash -c $(SCRIPT_NAT_DCKR)
	bash -c $(DCKR_EXIT)


	exit 0
	cd code/sys_test; \
		$(PYTHON) \
			generate_timings.py
	#	docker run bitcoind
	# 	time docke exec bitcoin-cli setgernate
	# time
	# 	bitcoind
	#	time bitcoin-cli setgenerate

# debugging the container

exp1_start:
	bash -c $(DCKR_INIT)
exp1_shell:
	docker exec -it simcoin_exp1 bash
exp1_stop:
	bash -c $(DCKR_EXIT)
