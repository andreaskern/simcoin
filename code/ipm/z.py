import fire
import subprocess
import time
from m import Machine


class Environment:
    network_create = lambda self: subprocess.call(
            f'/usr/bin/docker network create '
            f' --subnet=240.0.0.0/4 '
            f' --internal '
            f' --driver bridge simcoin-network '.split()
    )
    network_rm     = lambda self: subprocess.call(
        f'docker network rm simcoin-network'.split()
    )

    def run(self):
        self.network_create()
        # machines can be spawned directly or through the control node
        # control = run_machine_control
        m1 = Machine(1,"simcoin_ipm_machine","p.py")
        m1.create().start()
        m2 = Machine(2,"simcoin_ipm_machine","p.py")
        m2.create().start()

        input("Press Enter to continue...")

        startsignal = time.time() + 3 # in seconds

        m1.run_process(f"/usr/bin/python3.6 p.py run --id=1 --nodes=2 --start_at_timestamp={startsignal}")
        m2.run_process(f"/usr/bin/python3.6 p.py run --id=2 --nodes=2 --start_at_timestamp={startsignal}")

        # wait for container processes to exit
        m1.wait()
        m2.wait()

        print(m1.get_output_tape())
        print(m2.get_output_tape())

        m1.stop().rm()
        m2.stop().rm()

        print("SUCCESS")
        # adversary tries to prove some fault in the protocol
        # run_machine_adversary
        self.network_rm()
    
    def clean(self):
        self.network_rm()
        print("nop")

if __name__ == '__main__':
  fire.Fire(Environment)