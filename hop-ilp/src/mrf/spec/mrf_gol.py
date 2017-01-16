from logger import logger
import mrf
from mrf.spec.mrf_base import BaseMRF
from mrf.mrf_clique import MRFClique
import math
import random


class GolMRF(BaseMRF):
    var_to_idx = {}  # Var is a tuple (name, future, horizon)
    idx_to_var = []
    constr_cats = ['init_states', 'init_actions', 'concurrency', 'transition', 'reward']
    constrs = {}

    neighbours = {}
    noise_probs = {}

    def __init__(self, *args, **kwargs):
        BaseMRF.__init__(self, *args, **kwargs)
        self.add_fixed_constrs()
        self.get_instance_params()
        if self.debug:
            logger.debug(self.problem.variables)
            logger.debug(self.problem.actions)
            logger.debug(self.neighbours)
            logger.debug(self.noise_probs)

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
                    # Clique: MSB[n1(h-1), n2(h-1),..., v(h-1), v(h), set(v, h-1)]LSB
                    neighbours = self.neighbours[v]
                    var_indices = [self.var_to_idx[(self.find_matching_action(v), k, h - 1)],
                                   self.var_to_idx[(v, k, h)], self.var_to_idx[(v, k, h - 1)]]
                    var_indices.extend([self.var_to_idx[(n, k, h - 1)] for n in neighbours])
                    num_vars = len(var_indices)
                    determinized_transition = {}

                    clique = MRFClique(var_indices)
                    clique.function_table = []

                    for clique_bitmask in range(2**num_vars):
                        dependencies_bitmask = ((clique_bitmask >> 2) << 1) | (clique_bitmask & 1)

                        if dependencies_bitmask in determinized_transition:
                            determinized_val = determinized_transition[dependencies_bitmask]
                        else:
                            is_set = (clique_bitmask & 1) != 0
                            num_set_neighbours = self.count_set_neighbours(clique_bitmask, len(neighbours))
                            is_alive = (clique_bitmask & 2) != 0

                            if (is_alive and num_set_neighbours in (2, 3)) \
                               or (not is_alive and num_set_neighbours == 3) \
                               or is_set:
                                if random.random() <= (1. - self.noise_probs[v]):
                                    determinized_val = 1
                                else:
                                    determinized_val = 0
                            else:
                                if random.random() <= self.noise_probs[v]:
                                    determinized_val = 1
                                else:
                                    determinized_val = 0

                            determinized_transition[dependencies_bitmask] = determinized_val

                        if (clique_bitmask & 2) >> 1 == determinized_val:
                            clique.function_table.append(1)
                        else:
                            clique.function_table.append(mrf.INVALID_POTENTIAL_VAL)

                    self.constrs['transition'].append(clique)

        logger.info('set_transition_constraints')

    @staticmethod
    def count_set_neighbours(clique_bitmask, num_neighbours):
        bit_pointer = 1 << 3
        count = 0

        for _ in range(num_neighbours):
            if clique_bitmask & bit_pointer > 0:
                count += 1
            bit_pointer <<= 1

        return count

    def add_reward_constrs(self):
        function_table = [math.exp(x) for x in [0, 1, -1, 0]]
        for k in range(self.num_futures):
            for h in range(self.problem.horizon):
                for v in self.problem.variables:
                    a = self.find_matching_action(v)
                    vars_indices = [self.var_to_idx[(v, k, h)],
                                    self.var_to_idx[(a, k, h)]]
                    clique = MRFClique(vars_indices)
                    clique.function_table = function_table
                    self.constrs['reward'].append(clique)

        logger.info('Added reward constraints')

    def get_instance_params(self):
        rddl_file = self.problem.file.replace('json', 'rddl')

        with open(rddl_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('NOISE-PROB'):
                    x, y = self.get_rddl_function_params(line, 'NOISE-PROB')
                    val = self.get_rddl_assignment_val(line, float)
                    self.noise_probs[self.var_from_coord(x, y)] = val
                elif line.startswith('NEIGHBOR'):
                    x, y, nx, ny = self.get_rddl_function_params(line, 'NEIGHBOR')
                    var = self.var_from_coord(x, y)
                    if var not in self.neighbours:
                        self.neighbours[var] = []
                    self.neighbours[var].append(self.var_from_coord(nx, ny))

    @staticmethod
    def var_from_coord(x, y):
        return 'alive__%s_%s' % (x, y)

    @staticmethod
    def find_matching_action(state):
        return 'set%s' % (state[state.rindex('__'):],)
