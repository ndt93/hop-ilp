from logger import logger
import mrf
from mrf.mrf_clique import MRFClique
from mrf.mplp_runner import MPLPRunner
import mrf.utils as utils
from mrf.utils import count_set_bits, stringify, write_line
import math
import re
import random


class SysAdminMRF(object):
    REBOOT_PENALTY = 0.75
    REBOOT_PROB = 0.1
    topology = {}

    var_to_idx = {}  # Var is a tuple (name, future, horizon)
    idx_to_var = []
    constr_cats = ['init_states', 'init_actions', 'concurrency', 'transition', 'reward']
    constrs = {}

    def __init__(self, problem_name, problem, num_futures, time_limit=None, debug=False):
        logger.info('Initializing problem...')
        self.problem_name = problem_name
        self.problem = problem
        self.num_futures = num_futures
        self.time_limit = time_limit
        self.debug = debug

        self.map_vars_to_indices(problem, num_futures)
        self.mplp_runner = MPLPRunner(self.problem.actions, self.idx_to_var, time_limit)
        self.constrs = {cat: [] for cat in self.constr_cats}
        self.get_network_params()
        if self.debug:
            print('TOPOLOGY:\n%s\n' % self.topology)
            print('REBOOT-PROB: %s\n' % self.REBOOT_PROB)
        self.add_fixed_constrs()
        logger.info('Done initializing!')

    def solve(self):
        self.set_init_states_constrs(self.problem.variables)
        self.set_transition_constrs()

        self.write_mrf(mrf.OUTPUT_FILE)
        map_assignments = self.mplp_runner.run_mplp()
        #utils.print_MAP(map_assignments, self.problem, self.num_futures)
        next_actions = self.mplp_runner.get_next_actions(map_assignments)

        logger.info('next_action|states={},actions={}'.format(self.problem.variables, next_actions))
        return next_actions, None

    def init_next_step(self, states):
        self.problem.variables.update(states)

    def write_mrf(self, filename):
        with open(filename, 'w') as f:
            write_line(f, mrf.PREAMBLE)
            write_line(f, len(self.idx_to_var))
            write_line(f, ' '.join(['2'] * len(self.idx_to_var)))

            num_cliques = sum([len(self.constrs[cliques]) for cliques in self.constrs])
            write_line(f, num_cliques)

            for cat, cliques in self.constrs.items():
                #write_line(f, '<%s>' % cat)
                for clique in cliques:
                    self.write_clique_vars_list(f, clique)
                #write_line(f, '</%s>' % cat)

            for cat, cliques in self.constrs.items():
                #write_line(f, '<%s>' % cat)
                for clique in cliques:
                    self.write_clique_function_table(f, clique)
                #write_line(f, '</%s>' % cat)

        logger.info('write_model_to_file|f={}'.format(filename))

    @staticmethod
    def write_clique_vars_list(f, clique):
        f.write('{} {}\n'.
                format(len(clique.vars),
                       ' '.join(stringify(clique.vars[::-1]))))

    @staticmethod
    def write_clique_function_table(f, clique):
        f.write('{} {}\n'.
                format(len(clique.function_table),
                       ' '.join(stringify(clique.function_table))))

    def map_vars_to_indices(self, problem, num_futures):
        logger.info('Mapping variables to indices...')
        for state in problem.variables:
            for k in range(num_futures):
                for h in range(problem.horizon):
                    self.add_var((state, k, h))

        for action in problem.actions:
            for k in range(num_futures):
                for h in range(problem.horizon):
                    self.add_var((action, k, h))

        for k in range(num_futures):
            for h in range(problem.horizon):
                self.add_var(('__r__', k, h))

        if self.debug:
            print(self.var_to_idx)
            print(self.idx_to_var)

    def add_var(self, var):
        self.idx_to_var.append(var)
        self.var_to_idx[var] = len(self.idx_to_var) - 1

    def add_variable_constrs(self, init_state_vals):
        self.set_init_states_constrs(init_state_vals)
        self.set_transition_constrs()

    def set_init_states_constrs(self, init_state_vals):
        self.constrs['init_states'] = []

        function_table_0 = [1, mrf.INVALID_POTENTIAL_VAL]
        function_table_1 = [mrf.INVALID_POTENTIAL_VAL, 1]

        for k in range(self.num_futures):
            for v in self.problem.variables:
                vars_indices = [self.var_to_idx[(v, k, 0)]]
                clique = MRFClique(vars_indices)
                if init_state_vals[v] == 0:
                    clique.function_table = function_table_0
                else:
                    clique.function_table = function_table_1
                self.constrs['init_states'].append(clique)

        logger.info('set_init_states_constraints')

    def set_transition_constrs(self):
        self.constrs['transition'] = []

        for k in range(self.num_futures):
            for h in range(1, self.problem.horizon):
                for v in self.problem.variables:
                    # Clique: MSB[n1(h-1), n2(h-1),..., v(h-1), v(h), reboot(v, h-1)]LSB
                    neighbours = self.topology[v]
                    var_indices = [self.var_to_idx[(self.find_matching_action(v), k, h - 1)],
                                   self.var_to_idx[(v, k, h)], self.var_to_idx[(v, k, h - 1)]]
                    var_indices.extend([self.var_to_idx[(n, k, h - 1)] for n in neighbours])
                    num_vars = len(var_indices)
                    determinized_transition = {}

                    clique = MRFClique(var_indices)
                    clique.function_table = []

                    for clique_bitmask in range(2**num_vars):
                        if clique_bitmask & 1 != 0:
                            if clique_bitmask & 2 != 0:
                                clique.function_table.append(1)
                            else:
                                clique.function_table.append(mrf.INVALID_POTENTIAL_VAL)
                        else:
                            dependencies_bitmask = clique_bitmask >> 2

                            if dependencies_bitmask in determinized_transition:
                                determinized_val = determinized_transition[dependencies_bitmask]
                            else:
                                if clique_bitmask & 4 != 0:
                                    running_neighbours = self.count_set_neighbours(clique_bitmask,
                                                                                   num_vars - 2)
                                    running_prob = 0.45 + 0.5*(1 + running_neighbours)/(1 + len(neighbours))

                                    if random.random() <= running_prob:
                                        determinized_val = 1
                                    else:
                                        determinized_val = 0
                                else:
                                    if random.random() <= self.REBOOT_PROB:
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

    def add_fixed_constrs(self):
        self.add_concurrency_constrs()
        self.add_init_actions_constrs()
        self.add_reward_constrs()

    def add_concurrency_constrs(self):
        function_table = []
        for i in range(2**len(self.problem.actions)):
            if count_set_bits(i) > self.problem.max_concurrency:
                function_table.append(mrf.INVALID_POTENTIAL_VAL)
            else:
                function_table.append(1)

        for k in range(self.num_futures):
            for h in range(self.problem.horizon):
                vars_indices = [self.var_to_idx[(action, k, h)]
                                for action in self.problem.actions]
                clique = MRFClique(vars_indices)
                clique.function_table = function_table
                self.constrs['concurrency'].append(clique)

        logger.info('Added concurrency constraints')

    def add_init_actions_constrs(self):
        function_table = []
        allset = 2**self.num_futures - 1
        for i in range(2**self.num_futures):
            if i == 0 or i == allset:
                function_table.append(1)
            else:
                function_table.append(mrf.INVALID_POTENTIAL_VAL)

        for action in self.problem.actions:
            vars_indices = [self.var_to_idx[(action, k, 0)]
                            for k in range(self.num_futures)]
            clique = MRFClique(vars_indices)
            clique.function_table = function_table
            self.constrs['init_actions'].append(clique)

        logger.info('Added concurrency constraints')

    def add_reward_constrs(self):
        function_table = [math.exp(x) for x in
                          [0, 1, -self.REBOOT_PENALTY, 1 - self.REBOOT_PENALTY]]
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

    @staticmethod
    def find_matching_action(state):
        return 'reboot%s' % (state[state.rindex('__'):],)

    def get_network_params(self):
        rddl_file = self.problem.file.replace('json', 'rddl')

        with open(rddl_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('computer'):
                    self.topology = self.init_computers_list(line)
                elif line.startswith('REBOOT-PROB'):
                    self.REBOOT_PROB = self.get_rddl_assignment_val(line, float)
                elif line.startswith('CONNECTED'):
                    computers = self.get_rddl_function_params(line, 'CONNECTED')
                    assert(len(computers) == 2)
                    computers = ['running__%s' % c for c in computers]
                    self.topology[computers[1]].append(computers[0])

        logger.info('Read network parameters')

    @staticmethod
    def count_set_neighbours(clique_bitmask, num_neighbours):
        bit_pointer = 1 << 3
        count = 0

        for _ in range(num_neighbours):
            if clique_bitmask & bit_pointer > 0:
                count += 1
            bit_pointer <<= 1

        return count

    @staticmethod
    def init_computers_list(list_str):
        list_start = list_str.index('{') + 1
        list_end = list_str.rindex('}')
        computers = list_str[list_start:list_end].split(',')
        return {'running__%s' % computer: [] for computer in computers}

    @staticmethod
    def get_rddl_assignment_val(rddl_str, t):
        val_start = rddl_str.index('=') + 1
        val_end = rddl_str.rindex(';')
        return t(rddl_str[val_start:val_end])

    @staticmethod
    def get_rddl_function_params(rddl_str, func_name):
        params_match = re.search(r'%s\s*\((.*)\)' % (func_name,), rddl_str)
        params_str = params_match.group(1)
        return params_str.split(',')

