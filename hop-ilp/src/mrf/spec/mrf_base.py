from logger import logger
import mrf
from mrf.mplp_runner import MPLPRunner
from mrf.mrf_clique import MRFClique
import mrf.utils as utils
import re


class BaseMRF(object):
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
        self.constrs = {cat: [] for cat in self.constr_cats}
        self.mplp_runner = MPLPRunner(self.problem.actions, self.idx_to_var, time_limit)

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

    def add_reward_constrs(self):
        logger.warn('add_reward_constrs is not implemented by subclass %s' % self.__class__.__name__)

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
