from logger import logger
import mrf
from mrf.spec.mrf_base import BaseMRF
from mrf.mrf_clique import MRFClique
import mrf.utils as utils
import random
import math
import re


class CopycatMRF(BaseMRF):

    def __init__(self, *args, **kwargs):
        BaseMRF.__init__(self, *args, **kwargs)
        self.inst_params = {
            'prev': {},
            'xs': [],
            'ys': [],
        }

        self.get_instance_params()
        self.add_fixed_constrs()

        if self.debug:
            logger.debug(self.problem.variables)
            logger.debug(self.problem.actions)
            logger.debug(self.inst_params)

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
                xindices = [self.var_to_idx[x, k, h-1] for x in self.inst_params['xs']]
                aindices = [self.var_to_idx[a, k, h-1] for a in self.problem.actions]
                num_xs = len(xindices)

                for x in self.inst_params['xs']:
                    clique = MRFClique([self.var_to_idx[x, k, h]])
                    determinized_val = 1 if random.random() < 0.5 else 0
                    utils.append_function_entry(clique, 0, 0, determinized_val)
                    utils.append_function_entry(clique, 1, 0, determinized_val)
                    self.constrs['transition'].append(clique)

                for y in self.inst_params['ys']:
                    var_indices = [self.var_to_idx[y, k, h], self.var_to_idx[y, k, h-1]]
                    var_indices.extend(xindices)
                    var_indices.extend(aindices)
                    clique = MRFClique(var_indices)
                    for bitmask in range(2**len(var_indices)):
                        if utils.is_set(bitmask, 1):
                            utils.append_function_entry(clique, bitmask, 0, 1)
                            continue

                        matched = True
                        for i in range(2, 2+num_xs):
                            if utils.is_set(bitmask, i) != utils.is_set(bitmask, i+num_xs):
                                matched = False
                                break
                        if matched and random.random() < 0.49:
                            utils.append_function_entry(clique, bitmask, 0, 1)
                        else:
                            utils.append_function_entry(clique, bitmask, 0, 0)
                    self.constrs['transition'].append(clique)

        logger.info('set_transition_constraints')

    def add_reward_constrs(self):
        for k in range(self.num_futures):
            for h in range(self.problem.horizon):
                for y in self.inst_params['ys']:
                    clique = MRFClique([self.var_to_idx[y, k, h]])
                    clique.function_table = [math.exp(i) for i in [0, 1]]
                    self.constrs['reward'].append(clique)

        logger.info('Added reward constraints')

    def get_instance_params(self):
        rddl_file = self.problem.file.replace('json', 'rddl')
        with open(rddl_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('x_index'):
                    x_indices = self.get_rddl_list(line)
                    self.inst_params['xs'] = [self.idx_to_xstate(idx) for idx in x_indices]
                elif line.startswith('y_index'):
                    y_indices = self.get_rddl_list(line)
                    self.inst_params['ys'] = [self.idx_to_ystate(idx) for idx in y_indices]
                elif line.startswith('PREV'):
                    prev, cur = [self.idx_to_ystate(y) for y in self.get_rddl_function_params(line, 'PREV')]
                    self.inst_params['prev'][cur] = prev

        self.inst_params['xs'].sort()
        self.problem.actions.sort()

    @staticmethod
    def get_rddl_list(line):
        list_str = line[line.index('{')+1:line.rindex('}')]
        return re.split(r'\W+', list_str.strip())

    @staticmethod
    def idx_to_ystate(idx):
        return 'y__%s' % (idx)

    @staticmethod
    def idx_to_xstate(idx):
        return 'x__%s' % (idx)
