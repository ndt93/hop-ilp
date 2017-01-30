from logger import logger
import mrf
from mrf.spec.mrf_base import BaseMRF
from mrf.mrf_clique import MRFClique
import mrf.utils as utils
import random
import math
import re


class ElevatorsMRF(BaseMRF):
    inst_params = {
        'elevators': [],
        'floors': [],
    }

    def __init__(self, *args, **kwargs):
        BaseMRF.__init__(self, *args, **kwargs)
        self.get_instance_params()
        self.add_fixed_constrs(concurrency=True)
        if self.debug:
            logger.debug(self.problem.variables)
            logger.debug(self.problem.actions)
            logger.debug(self.inst_params)

    def solve(self):
        self.set_init_states_constrs(self.problem.variables)
        self.set_transition_constrs()

        self.write_mrf(mrf.OUTPUT_FILE)
        map_assignments = self.mplp_runner.run_mplp()
        next_actions = self.mplp_runner.get_next_actions(map_assignments)

        logger.info('next_action|states={},actions={}'.format(self.problem.variables, next_actions))
        return next_actions, None

    def init_next_step(self, states):
        self.problem.variables.update(states)

    def set_transition_constrs(self):
        self.constrs['transition'] = []

        for k in range(self.num_futures):
            for h in range(1, self.problem.horizon):
                pass
        logger.info('set_transition_constraints')

    def add_reward_constrs(self):
        for k in range(self.num_futures):
            for h in range(self.problem.horizon):
                pass
        logger.info('Added reward constraints')

    def get_instance_params(self):
        rddl_file = self.problem.file.replace('json', 'rddl')
        with open(rddl_file, 'r') as f:
            for line in f:
                line = line.strip()
                if re.match(r'elevator\s*:', line):
                    self.inst_params['elevators'] = self.get_rddl_list(line)
                elif line.startswith('floor'):
                    self.inst_params['floors'] = self.get_rddl_list(line)

    @staticmethod
    def get_rddl_list(line):
        list_str = line[line.index('{')+1:line.rindex('}')]
        return list_str.split(',')
