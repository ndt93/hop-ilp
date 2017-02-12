from gurobipy import *
from solver.spec.ilp_base import ILPBase
import utils
from logger import logger
import random


class ILPCopycat(ILPBase):

    def __init__(self, *args, **kwargs):
        super(ILPCopycat, self).__init__(*args, **kwargs)
        self.inst_params = {
            'prev': {},
            'xs': [],
            'ys': [],
        }
        self.get_instance_params()
        self.add_reward_objective()

    def set_transition_constrs(self):
        self.reset_transition_constrs()
        xs = self.inst_params['xs']
        actions = self.problem.actions

        for k in range(self.num_futures):
            for h in range(1, self.problem.horizon):
                for x in self.inst_params['xs']:
                    determinized_val = 1 if random.random() < 0.5 else 0
                    constr = self.model.addConstr(self.all_vars[x, k, h] == determinized_val,
                                                  name='transition:%s^%d^%d' % (x, k, h))
                    self.constrs['transition'].append(constr)

                for y in self.inst_params['ys']:
                    paths = [[(y, 1)]]
                    for bitmask in range(2**len(xs)):
                        if random.random() >= 0.49:
                            continue
                        path = utils.make_path(xs, bitmask)
                        path.extend(utils.make_path(actions, bitmask))
                        paths.append(path)
                    self.paths_to_transition_constrs(paths, k, h, y)

        logger.info('set_transition_constrs')

    def add_reward_objective(self):
        for k in range(self.num_futures):
            for h in range(self.problem.horizon):
                for y in self.inst_params['ys']:
                    paths = self.str_paths_to_var_paths([[(y, 0)], [(y, 1)]], k, h)
                    leaves = (0, 1)
                    self.paths_to_reward_constrs(paths, leaves, k, h)

        self.model.ModelSense = GRB.MAXIMIZE
        logger.info('added_reward_objective')

    def get_disappear_prob(self, v):
        return self.inst_params['probs'].get(v, 0.)

    def get_instance_params(self):
        rddl_file = self.problem.file.replace('json', 'rddl')
        with open(rddl_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('x_index'):
                    x_indices = utils.get_rddl_list(line)
                    self.inst_params['xs'] = [self.idx_to_xstate(idx) for idx in x_indices]
                elif line.startswith('y_index'):
                    y_indices = utils.get_rddl_list(line)
                    self.inst_params['ys'] = [self.idx_to_ystate(idx) for idx in y_indices]
                elif line.startswith('PREV'):
                    prev, cur = [self.idx_to_ystate(y)
                                 for y in utils.get_rddl_function_params(line, 'PREV')]
                    self.inst_params['prev'][cur] = prev

        self.inst_params['xs'].sort()
        self.problem.actions.sort()

    @staticmethod
    def idx_to_ystate(idx):
        return 'y__%s' % (idx)

    @staticmethod
    def idx_to_xstate(idx):
        return 'x__%s' % (idx)

