from logger import logger
import mrf
from mrf.mrf_clique import MRFClique
from mrf import utils
import math
import re


class SysAdminMRF(object):
    REBOOT_PENALTY = 0.75
    REBOOT_PROB = 0.1
    topology = {}

    var_to_idx = {}  # Var is a tuple (name, future, horizon)
    idx_to_var = []
    constrs = {
        'init_states': [],
        'init_actions': [],
        'concurrency': [],
        'transition': [],
        'reward': [],
    }

    def __init__(self, problem, num_futures, time_limit=None, debug=False):
        logger.info('Initializing problem...')
        self.problem = problem
        self.num_futures = num_futures
        self.time_limit = time_limit
        self.debug = debug

        self.map_vars_to_indices(problem, num_futures)
        self.get_network_params()
        print('TOPOLOGY:\n%s\n' % self.topology)
        print('REBOOT-PROB: %s\n' % self.REBOOT_PROB)
        self.add_fixed_constrs()
        logger.info('Done initializing!')

    def solve(self, init_state_vals):
        pass

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

    def add_fixed_constrs(self):
        self.add_concurrency_constrs()
        self.add_init_actions_constrs()
        self.add_reward_constrs()

    def add_variable_constrs(self, init_state_vals):
        self.set_init_states_constrs(init_state_vals)
        self.set_transition_constrs()

    def set_init_states_constrs(self, init_state_vals):
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

    def set_transition_constrs(self):
        pass

    def add_concurrency_constrs(self):
        function_table = []
        for i in range(2**len(self.problem.actions)):
            if utils.count_set_bits(i) > self.problem.max_concurrency:
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
                    self.topology[computers[1]].append(computers[0])
        logger.info('Read network parameters')

    @staticmethod
    def init_computers_list(list_str):
        list_start = list_str.index('{') + 1
        list_end = list_str.rindex('}')
        computers = list_str[list_start:list_end].split(',')
        return {computer: [] for computer in computers}

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
