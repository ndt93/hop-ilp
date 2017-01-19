from logger import logger
import mrf
from mrf.spec.mrf_base import BaseMRF
from mrf.mrf_clique import MRFClique
import math
import random
import re


class NavMRF(BaseMRF):
    var_to_idx = {}  # Var is a tuple (name, future, horizon)
    idx_to_var = []
    constr_cats = ['init_states', 'init_actions', 'concurrency', 'transition', 'reward']
    constrs = {}

    grid = {}
    probs = {}
    boundary = {}

    def __init__(self, *args, **kwargs):
        BaseMRF.__init__(self, *args, **kwargs)
        self.get_instance_params()
        self.add_fixed_constrs()
        if self.debug:
            logger.debug(self.problem.variables)
            logger.debug(self.problem.actions)
            logger.debug(self.grid)
            logger.debug(self.probs)
            logger.debug(self.boundary)

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
        # TODO: incomplete
        logger.info('set_transition_constraints')

    @staticmethod
    def count_set_neighbours(clique_bitmask, num_neighbours):
        # TODO: May not need
        bit_pointer = 1 << 3
        count = 0

        for _ in range(num_neighbours):
            if clique_bitmask & bit_pointer > 0:
                count += 1
            bit_pointer <<= 1

        return count

    def add_reward_constrs(self):
        # TODO: incomplete
        logger.info('Added reward constraints')

    def get_instance_params(self):
        rddl_file = self.problem.file.replace('json', 'rddl')
        with open(rddl_file, 'r') as f:
            for line in f:
                line = line.strip()

                if line.startswith('P'):
                    x, y = self.get_rddl_function_params(line, 'P')
                    prob = self.get_rddl_assignment_val(line, float)
                    self.probs[self.get_state_from_coords(x, y)] = prob
                    continue

                dir_match = re.match(r'(NORTH|EAST|SOUTH|WEST)', line)
                if dir_match:
                    dir = dir_match.group(1)
                    y, ny = self.get_rddl_function_params(line, dir)
                    if y not in self.grid:
                        self.grid[y] = {}
                    self.grid[y][dir[0]] = ny
                    continue

                boundary_match = re.match(r'(MIN-XPOS|MAX-XPOS|MIN-YPOS|MAX-YPOS)', line)
                if boundary_match:
                    terminal = boundary_match.group(1)
                    coord = self.get_rddl_function_params(line, terminal)
                    self.boundary[terminal] = coord

    @staticmethod
    def get_state_from_coords(x, y):
        return 'robot_at__%s_%s' % (x, y)
