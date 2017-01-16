from logger import logger
from mrf.spec.mrf_base import BaseMRF
from mrf.mrf_clique import MRFClique
import math


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

    @staticmethod
    def find_matching_action(state):
        return 'set%s' % (state[state.rindex('__'):],)
