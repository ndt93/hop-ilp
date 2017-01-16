from logger import logger
import mrf
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
        if self.debug:
            logger.debug(self.problem.variables)
            logger.debug(self.problem.actions)
            logger.debug(self.neighbours)
            logger.debug(self.noise_probs)

    def solve(self):
        self.set_init_states_constrs(self.problem.variables)
        self.set_transition_constrs()

        # self.write_mrf(mrf.OUTPUT_FILE)
        # map_assignments = self.mplp_runner.run_mplp()
        # next_actions = self.mplp_runner.get_next_actions(map_assignments)

        # logger.info('next_action|states={},actions={}'.format(self.problem.variables, next_actions))
        # return next_actions, None

    def init_next_step(self, states):
        self.problem.variables.update(states)

    def set_transition_constrs(self):
        pass

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
