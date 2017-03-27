from logger import logger
import mrf
from mrf.spec.mrf_base import BaseMRF
from mrf.mrf_clique import MRFClique
import mrf.utils as utils
import random
import math
import re


class NavMRF(BaseMRF):
    grid = {}
    probs = {}
    boundary = {}
    goal = None
    dir_to_action = {'NORTH': 'move_north', 'EAST': 'move_east',
                     'SOUTH': 'move_south', 'WEST': 'move_west'}
    opposite_action = {'move_north': 'move_south', 'move_south': 'move_north',
                       'move_east': 'move_west', 'move_west': 'move_east'}

    def __init__(self, *args, **kwargs):
        BaseMRF.__init__(self, *args, **kwargs)
        self.get_instance_params()
        self.add_fixed_constrs(concurrency=True)
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

        pos_actions = [a for a in next_actions if next_actions[a] == 1]
        if len(pos_actions) > self.problem.max_concurrency:
            off_actions = random.sample(pos_actions,
                                        len(pos_actions) - self.problem.max_concurrency)
            for a in off_actions:
                next_actions[a] = 0

        logger.info('next_action|states={},actions={}'.format(self.problem.variables, next_actions))
        return next_actions, None

    def init_next_step(self, states):
        self.problem.variables.update(states)

    def set_transition_constrs(self):
        """
        Each logical expression used to specify the transition function corresponds to a clique and
        an additional variable. If an entry in a clique is sufficient to decide the outcome of the
        next state or the outcome is already decided by earlier clauses, its extended variable is
        constrained to 1. Otherwise, it's constrained to 0.
        :return:
        """
        self.constrs['transition'] = []

        for k in range(self.num_futures):
            for h in range(1, self.problem.horizon):
                for v in self.problem.variables:
                    # If at goal stays at goal
                    clique = MRFClique([])
                    if v == self.goal:
                        clique.vars = [self.var_to_idx[(v, k, h)],
                                       self.var_to_idx[(v, k, h-1)]]
                        for bitmask in range(2**len(clique.vars)):
                            if utils.is_set(bitmask, 1):
                                if utils.is_set(bitmask, 0):
                                    clique.function_table.append(1)
                                else:
                                    clique.function_table.append(10**(-18))
                    else:
                        clique.vars = [self.var_to_idx[(v, k, h)],
                                       self.var_to_idx[(self.goal, k, h-1)]]
                        for bitmask in range(2**len(clique.vars)):
                            if utils.is_set(bitmask, 1):
                                if utils.is_set(bitmask, 0):
                                    clique.function_table.append(10**(-18))
                                else:
                                    clique.function_table.append(1)
                    self.constrs['transition'].append(clique)

                    x, y = self.get_coords_from_state(v)
                    all_actions = self.grid[x].keys() + self.grid[y].keys()

                    # Moving to neighbours
                    for level, action in enumerate(all_actions):
                        clique = MRFClique([self.var_to_idx[(v, k, h)],
                                            self.var_to_idx[(v, k, h-1)],
                                            self.var_to_idx[(action, k, h-1)]])

                        for bitmask in range(2**len(clique.vars)):
                            if utils.is_set(bitmask, 1) and utils.is_set(bitmask, 2):
                                if utils.is_set(bitmask, 0):
                                    clique.function_table.append(10**(-2))
                                else:
                                    clique.function_table.append(1)

                        self.constrs['transition'].append(clique)

                    # Moving from neighbours
                    for level, action in enumerate(all_actions):
                        neighbour_action = self.opposite_action[action]
                        nx, ny = x, y
                        if action in self.grid[x]:
                            nx = self.grid[x][action]
                        else:
                            ny = self.grid[y][action]
                        neighbour = self.get_state_from_coords(nx, ny)

                        clique = MRFClique([self.var_to_idx[(v, k, h)],
                                            self.var_to_idx[(neighbour, k, h-1)],
                                            self.var_to_idx[(neighbour_action, k, h-1)]])

                        for bitmask in range(2**len(clique.vars)):
                            if utils.is_set(bitmask, 1) and utils.is_set(bitmask, 2):
                                if random.random() < self.get_disappear_prob(v):
                                    determinized_val = 0
                                else:
                                    determinized_val = 1
                                if utils.is_set(bitmask, 0) == (determinized_val == 1):
                                    clique.function_table.append(1)
                                else:
                                    clique.function_table.append(10**-2)

                        self.constrs['transition'].append(clique)

                    # Otherwise keeps the same state
                    clique = MRFClique([self.var_to_idx[(v, k, h)],
                                        self.var_to_idx[(v, k, h-1)]])
                    for bitmask in range(2**len(clique.vars)):
                        if utils.is_set(bitmask, 0) == utils.is_set(bitmask, 1):
                            clique.function_table.append(1)
                        else:
                            clique.function_table.append(10**(-1))
                    self.constrs['transition'].append(clique)

        logger.info('set_transition_constraints')

    def get_disappear_prob(self, v):
        if v in self.probs:
            return self.probs[v]
        return 0

    def add_reward_constrs(self):
        for k in range(self.num_futures):
            for h in range(self.problem.horizon):
                clique = MRFClique([self.var_to_idx[(self.goal, k, h)]])
                clique.function_table = [math.exp(x) for x in [-1, 0]]
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
                    self.grid[y][self.dir_to_action[dir]] = ny
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
