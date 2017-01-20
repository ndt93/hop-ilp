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
    goal = None

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
            logger.debug(self.goal)

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
                for v in self.problem.variables:
                    # If at goal, stays at goal
                    if v == self.goal:
                        clique = MRFClique([self.var_to_idx[(v, k, h)], self.var_to_idx[(v, k, h - 1)]])
                        clique.function_table = [1, 1, mrf.INVALID_POTENTIAL_VAL, 1]
                        self.constrs['transition'].append(clique)
                    else:
                        clique = MRFClique([self.var_to_idx[(v, k, h)], self.var_to_idx[(self.goal, k, h - 1)]])
                        clique.function_table = [1, 1, 1, mrf.INVALID_POTENTIAL_VAL]
                        self.constrs['transition'].append(clique)

                    # Clique: LSB[v(h), v(h-1), g(h - 1), a(h-1), n(h-1)]MSB
                    #               1      2        4        8      16
                    common_vars = [self.var_to_idx[(v, k, h)],
                                   self.var_to_idx[(v, k, h - 1)],
                                   self.var_to_idx[(self.goal, k, h - 1)]]
                    x, y = self.get_coords_from_state(v)

                    # move_north to neighbor
                    if 'N' in self.grid[y]:
                        nx, ny = x, self.grid[y]
                        clique = MRFClique(common_vars[:])
                        clique.vars.extend([self.var_to_idx[('move-north', k, h - 1)],
                                            self.var_to_idx[(self.get_state_from_coords(nx, ny)), k, h - 1]])
                        for clique_bitmask in range(2**len(clique.vars)):
                            pass



        logger.info('set_transition_constraints')

    def add_reward_constrs(self):
        for k in range(self.num_futures):
            for h in range(self.problem.horizon):
                clique = MRFClique([self.var_to_idx[(self.goal, k, h)]])
                clique.function_table = [-1, 0]
                self.constrs['reward'].append(clique)
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

                if line.startswith('GOAL'):
                    x, y = self.get_rddl_function_params(line, 'GOAL')
                    self.goal = self.get_state_from_coords(x, y)

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

    @staticmethod
    def get_coords_from_state(state):
        coords_start = state.rindex('__')
        return state[coords_start + 2:].split('_')
