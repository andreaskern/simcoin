
import fire
import backtrace

backtrace.hook(
    reverse=False,
    align=True,
    strip_path=False,
    enable_on_envvar_only=False,
    on_tty=False,
    conservative=False,
    styles={})

import subprocess

class Machine():
    """ class description """
    prefix = "prefix"


    def __init__(self,id=1,name="ipm_machine",files_to_load=""):
        self.name = self.prefix + "_" + name + "_" + str(id)
        self.id = id
        self.ip = id + 1
        self.files_to_load = files_to_load
    
    def __del__(self):
        y = 2
        #TODO docker rm

    def create(self, demo=False):
        # ~1270ms
        self.check()
        # String -> conatiner_created
        # TODO network
        # TODO boostrap node
        # TODO fix IP
        if demo:
            self.bash(f"\
            docker create \
                --tty \
                --cap-add=NET_ADMIN \
                --name {self.name} \
                simcoin2:v0.0.3 \
                ")
        else:
            self.bash(f"\
            docker create \
                --tty \
                --cap-add=NET_ADMIN \
                --net=simcoin-network \
                --cap-add=NET_ADMIN \
                --name {self.name} \
                simcoin2:v0.0.3 \
                ")

        self.load(self.files_to_load)
        return self

    def load(self, files):
        if files:
            files_str = files.split(" ")
            for ffile in files_str:
                self.bash(f"docker cp {ffile} {self.name}:/ ")


    def start(self):
        # ~780ms
        return self.bash(f"docker start {self.name} ")

    def stop(self):
        # ~730ms
        self.bash(f"docker stop {self.name} ")
        return self

    def rm(self):
        # ~390ms
        return self.bash(f"docker rm {self.name}")

    def nop(self):
        return NotImplemented

    def run_process(self,file_to_call):
        self.exec(f"{file_to_call}")
        return 

    def exec(self,file="ls"):
        # only on started conatiners
        # ~350ms
        self.p = subprocess.Popen( f"docker exec -it {self.name} {file} ".split())
        return self.p
    
    def wait(self):
        self.p.wait()

    def check(self):
        container_id = self.bash(f"docker ps -q -a -f name={self.name}")
        if "" != container_id:
            raise Exception("Docker instance already exists, cleanup first")
        else:
            return True

    def get_output_tape(self):
        return self.bash(f"docker exec -it {self.name} cat output.tape")

    @classmethod
    def clean(cls):
        containers = cls.bash("docker ps -q -a --format {{.Names}}")
        for name in containers.splitlines():
            if (name.startswith(cls.prefix)):
                cls.bash(f"docker rm -f {name}")
        return containers

    @classmethod
    def bash(cls,cmd):
        output = subprocess.check_output(
            cmd, 
            shell=True, 
            executable='/bin/bash',
            stderr = subprocess.STDOUT
            )
        encoded_output = output.decode('utf-8').rstrip()
        return encoded_output
    
    @classmethod
    def image_build(cls):
        # ddocker create some base image container
        # exec installs
        cls.bash(f"docker create --tty --name simcoin2_build_container ubuntu:xenial-20170119 ")
        cls.bash(f"docker start simcoin2_build_container ")

        cls.bash(f"docker exec -it simcoin2_build_container apt-get update ")

        cls.bash(f"docker exec -it simcoin2_build_container apt-get -y install software-properties-common ")
        cls.bash(f"docker exec -it simcoin2_build_container add-apt-repository -y ppa:bitcoin/bitcoin ")
        cls.bash(f"docker exec -it simcoin2_build_container add-apt-repository -y ppa:deadsnakes/ppa ") # python3.6

        cls.bash(f"docker exec -it simcoin2_build_container apt-get update ")


        cls.bash(
            """ 
            docker exec -it simcoin2_build_container \
                apt-get -y install \
                        build-essential \
                        libtool \
                        autotools-dev \
                        automake \
                        pkg-config \
                        libssl-dev \
                        libevent-dev\
                        bsdmainutils \
                        git \
                        \
                        libboost-system-dev \
                        libboost-filesystem-dev \
                        libboost-chrono-dev \
                        libboost-program-options-dev \
                        libboost-test-dev \
                        libboost-thread-dev \
                        \
                        libdb4.8-dev \
                        libdb4.8++-dev \
                        \
                        libssl-dev \

            """
            ## notest for the last two blocks:
            # from the ppa
            # for python-bitcoinli

        )

        cls.bash(f"docker exec -it simcoin2_build_container git clone --branch 0.17 https://github.com/bitcoin/bitcoin.git /bitcoin")
        cls.bash(f"docker exec -it simcoin2_build_container sh -c ' cd /bitcoin; ./autogen.sh' ")
        cls.bash(f"docker exec -it simcoin2_build_container sh -c ' cd /bitcoin; ./configure' ")
        cls.bash(f"docker exec -it simcoin2_build_container sh -c ' cd /bitcoin; make -j4 ' ")
        cls.bash(f"docker exec -it simcoin2_build_container sh -c ' cd /bitcoin; make install ' ") 
        ### this install `bitcoin-cli` `/usr/local/bin/bitcoin-cli`

        cls.bash(f"docker exec -it simcoin2_build_container apt-get -y install python3.6 python3-pip")
        cls.bash(f"docker exec -it simcoin2_build_container python3.6 -mpip install --upgrade pip")
        cls.bash(f"docker exec -it simcoin2_build_container pip3.6 install fire backtrace bitcoin")

        cls.bash(f"docker stop simcoin2_build_container ")
        cls.bash(f"docker commit simcoin2_build_container simcoin2:v0.0.1 ")
        cls.bash(f"docker rm simcoin2_build_container ")


        ## add missing python bitcoin rpc lib
        cls.bash(f"docker create --tty --name simcoin2_build_container simcoin2:v0.0.1 ")
        cls.bash(f"docker start simcoin2_build_container ")

        cls.bash(f"docker exec -it simcoin2_build_container pip3.6 install python-bitcoinrpc python-bitcoinlib")

        cls.bash(f"docker stop simcoin2_build_container ")
        cls.bash(f"docker commit simcoin2_build_container simcoin2:v0.0.2")
        cls.bash(f"docker rm simcoin2_build_container ")

        ## add iproute2 to enable tc (traffic control)

        cls.bash(f"""
            docker create --tty --name simcoin2_build_container simcoin2:v0.0.2
            docker start simcoin2_build_container

            docker exec -it simcoin2_build_container apt install iproute2

            docker stop simcoin2_build_container
            docker commit simcoin2_build_container simcoin2:v0.0.3
            docker rm simcoin2_build_container
        """)

        return True
    
    @classmethod
    def image_rm(cls):
        return cls.bash("docker rmi simcoin")

    @classmethod
    def info(cls):
        msg = []
        msg.extend([
            "#containers"
            , cls.bash(f"docker ps --quiet --all --filter name={cls.prefix} --format " + "\"({{.ID}}) {{.Names}}: {{.Status}} {{.Command}}\"")
        ])
        msg.append("#images")
        msg.extend( cls.bash(f"docker images simcoin2 --quiet --all   --format " + "\"({{.ID}}) {{.Repository}}: {{.Tag}}\"").split('\n'))
        return msg

    def debug_start(self): 
        self.create(demo=True)
        self.load("p.py")
        self.start()

    def debug_stop(self):
        self.stop()
        self.rm()

    def test(self):
        self.debug_start()
        self.debug_stop()
        return True


if __name__ == '__main__':
  fire.Fire(Machine)
