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
    dir_to_action = {'NORTH': 'move_north', 'EAST': 'move_east',
                     'SOUTH': 'move_south', 'WEST': 'move_west'}
    opposite_action = {'move_north': 'move_south', 'move_south': 'move_north',
                       'move_east': 'move_west', 'move_west': 'move_east'}

    def __init__(self, *args, **kwargs):
        BaseMRF.__init__(self, *args, **kwargs)
        self.get_instance_params()
        self.add_fixed_constrs(concurrency=False)
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
                    # Clique: LSB{v(h), v(h-1)[, g(h-1)], move-*(h-1),..., n(h-1),...}MSB
                    x, y = self.get_coords_from_state(v)
                    var_indices = [self.var_to_idx[(v, k, h)], self.var_to_idx[(v, k, h - 1)]]

                    if v != self.goal:
                        var_indices.append(self.var_to_idx[(self.goal, k, h - 1)])

                    action_to_bit_idx = {}
                    action_bit_idx_start = len(var_indices)
                    actions = self.grid[x].keys() + self.grid[y].keys()
                    for action in actions:
                        if action in action_to_bit_idx:
                            continue
                        action_to_bit_idx[action] = len(var_indices)
                        var_indices.append(self.var_to_idx[(action, k, h - 1)])
                        action_to_bit_idx[self.opposite_action[action]] = len(var_indices)
                        var_indices.append(self.var_to_idx[(self.opposite_action[action], k, h - 1)])

                    neighbor_info = {} # {n: [action to reach v from n, idx]}
                    neighbor_bit_idx_start = len(var_indices)
                    for action in self.grid[x]:
                        nx, ny = self.grid[x][action], y
                        n = self.get_state_from_coords(nx, ny)
                        neighbor_info[n] = [action_to_bit_idx[self.opposite_action[action]], len(var_indices)]
                        var_indices.append(self.var_to_idx[(n, k, h - 1)])
                    for action in self.grid[y]:
                        nx, ny = x, self.grid[y][action]
                        n = self.get_state_from_coords(nx, ny)
                        neighbor_info[n] = [action_to_bit_idx[self.opposite_action[action]], len(var_indices)]
                        var_indices.append(self.var_to_idx[(n, k, h - 1)])

                    for clique_bitmask in range(2**len(var_indices)):
                        clique = MRFClique(var_indices)
                        # Concurrency constraints
                        num_set_action = self.count_set_bit(clique_bitmask,
                                                            action_bit_idx_start, neighbor_bit_idx_start)
                        if num_set_action > self.problem.max_concurrency:
                            clique.function_table.append(mrf.INVALID_POTENTIAL_VAL)
                            self.constrs['transition'].append(clique)
                            continue

                        # At most 1 state is set
                        num_set_state = self.count_set_bit(clique_bitmask,
                                                           neighbor_bit_idx_start, len(var_indices))
                        num_set_state += 1 if clique_bitmask & 2 != 0 else 0
                        num_set_state += 1 if v != self.goal and clique_bitmask & 4 != 0 else 0
                        if num_set_state > 1:
                            clique.function_table.append(mrf.INVALID_POTENTIAL_VAL)
                            self.constrs['transition'].append(clique)
                            continue

                        # If at goal, stays at goal
                        if v == self.goal and clique_bitmask & 2 != 0:
                            if clique_bitmask & 1 != 0:
                                clique.function_table.append(1)
                            else:
                                clique.function_table.append(mrf.INVALID_POTENTIAL_VAL)
                            self.constrs['transition'].append(clique)
                            continue
                        if clique_bitmask & 4 != 0:
                            if clique_bitmask & 1 != 0:
                                clique.function_table.append(mrf.INVALID_POTENTIAL_VAL)
                            else:
                                clique.function_table.append(1)
                            self.constrs['transition'].append(clique)
                            continue

                        # Move to neighbors
                        if clique_bitmask & 2 != 0:
                            set_func_table = False
                            for action in actions:
                                if clique_bitmask & (1 << action_to_bit_idx[action]) != 0:
                                    if clique_bitmask & 1 == 0:
                                        clique.function_table.append(1)
                                    else:
                                        clique.function_table.append(mrf.INVALID_POTENTIAL_VAL)
                                    set_func_table = True
                                    break
                            if set_func_table:
                                self.constrs['transition'].append(clique)
                                continue
                        # Move from neighbors
                        else:
                            set_func_table = False
                            for neighbor in neighbor_info:
                                is_at_neighbor = (clique_bitmask & (1 << neighbor_info[neighbor][1])) != 0
                                is_action_set = (clique_bitmask & (1 << neighbor_info[neighbor][0])) != 0
                                if is_at_neighbor and is_action_set:
                                    if random.random() < self.get_disappear_prob(v):
                                        determinized_val = 0
                                    else:
                                        determinized_val = 1

                                    if (clique_bitmask & 1) == determinized_val:
                                        clique.function_table.append(1)
                                    else:
                                        clique.function_table.append(mrf.INVALID_POTENTIAL_VAL)
                                    set_func_table = True
                                    break
                            if set_func_table:
                                self.constrs['transition'].append(clique)
                                continue

                        if (clique_bitmask & 1) == ((clique_bitmask >> 1) & 1):
                            clique.function_table.append(1)
                        else:
                            clique.function_table.append(mrf.INVALID_POTENTIAL_VAL)
                        self.constrs['transition'].append(clique)

        logger.info('set_transition_constraints')

    def get_disappear_prob(self, v):
        if v in self.probs:
            return self.probs[v]
        return 0

    @staticmethod
    def count_set_bit(bitmask, start, end):
        """
        Counts number of set bit in bitmask[start:end]
        """
        count = 0
        i = 1 << start
        for _ in range(end - start):
            if bitmask & i != 0:
                count += 1
            i <<= 1
        return count

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
