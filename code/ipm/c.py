import subprocess
import fire
from m import Machine

class Control:
    """ spawns new machines, controls network """

    def __init__(self):
        self.machines = []
        # TODO create bridge
        # subprocess.Popen(["docker","bridge","create"])

    # def __del__(self):
    #     # TODO rm nodes
    #     # TODO rm bridge
    #     # subprocess.Popen(["docker","bridge","rm"])

    def msg_spawn(self):
        # TODO spawn nodes
        m = Machine()
        m.run_process("p.py")
        self.machines.append(m)

    def test(self):
        True

    def clean(self):
        subprocess.Popen(["docker","bridge","rm"])


if __name__ == '__main__':
  fire.Fire(Control)
    