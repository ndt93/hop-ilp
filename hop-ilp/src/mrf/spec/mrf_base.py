from logger import logger
import mrf
from mrf.mplp_runner import MPLPRunner
from mrf.mrf_clique import MRFClique
import mrf.utils as utils
import re


class BaseMRF(object):
    def __init__(self, problem_name, problem, num_futures, time_limit=None, debug=False):
        logger.info('Initializing problem...')

        self.var_to_idx = {}  # Var is a tuple (name, future, horizon)
        self.idx_to_var = []
        self.constr_cats = ['init_states', 'init_actions', 'concurrency', 'transition', 'reward']
        self.constrs = {}

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

    def add_var(self, var):
        self.idx_to_var.append(var)
        self.var_to_idx[var] = len(self.idx_to_var) - 1

    def add_fixed_constrs(self, concurrency=True):
        if concurrency:
            self.add_concurrency_constrs()
        self.add_init_actions_constrs()
        self.add_reward_constrs()

    def add_concurrency_constrs(self):
        function_table = []
        for i in range(2**len(self.problem.actions)):
            if utils.count_set_bits(i) > self.problem.max_concurrency:
                function_table.append(mrf.INVALID_POTENTIAL_VAL_2)
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

        logger.info('Added init actions constraints')

    def set_init_states_constrs(self, init_state_vals):
        self.constrs['init_states'] = []

        function_table_0 = [1, mrf.INVALID_POTENTIAL_VAL_2]
        function_table_1 = [mrf.INVALID_POTENTIAL_VAL_2, 1]

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

    def write_mrf(self, filename):
        with open(filename, 'w') as f:
            utils.write_line(f, mrf.PREAMBLE)
            utils.write_line(f, len(self.idx_to_var))
            utils.write_line(f, ' '.join(['2'] * len(self.idx_to_var)))

            num_cliques = sum([len(self.constrs[cliques]) for cliques in self.constrs])
            utils.write_line(f, num_cliques)

            for cat, cliques in self.constrs.items():
                if len(cliques) == 0:
                    continue
                for clique in cliques:
                    self.write_clique_vars_list(f, clique)

            for cat, cliques in self.constrs.items():
                if len(cliques) == 0:
                    continue
                for clique in cliques:
                    self.write_clique_function_table(f, clique)

        logger.info('write_model_to_file|f={}'.format(filename))

    @staticmethod
    def write_clique_vars_list(f, clique):
        f.write('{} {}\n'.
                format(len(clique.vars),
                       ' '.join(utils.stringify(clique.vars[::-1]))))

    @staticmethod
    def write_clique_function_table(f, clique):
        f.write('{} {}\n'.
                format(len(clique.function_table),
                       ' '.join(utils.stringify(clique.function_table))))

