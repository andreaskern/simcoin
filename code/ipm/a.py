
class Adversary:

    def program(self, control_node):
        self.control_node = control_node
        self._scenario_1()


    def _scenario_1(self):
        control_node.m_exit_if_all_other_machines_exited()


