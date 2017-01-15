from logger import logger
from mrf.mplp_runner import MPLPRunner


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
