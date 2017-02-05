from gurobipy import *
from solver.spec.ilp_base import ILPBase
import utils
from logger import logger
import random


class ILPSysadmin(ILPBase):
    inst_params = {
        'topology': None,
        'REBOOT-PROB': 0.1,
        'REBOOT-PENALTY': 0.75,
    }

    def __init__(self, *args, **kwargs):
        super(ILPSysadmin, self).__init__(*args, **kwargs)
        self.get_instance_params()
        self.add_reward_objective()

    def set_transition_constrs(self):
        self.reset_transition_constrs()

        for k in range(self.num_futures):
            for h in range(1, self.problem.horizon):
                for v in self.problem.variables:
                    neighbours = self.inst_params['topology'][v]
                    reboot = self.find_matching_action(v)
                    paths = [[(reboot, 1)]]

                    for bitmask in range(2**len(neighbours)):
                        running_neighbours = utils.count_set_bits(bitmask)
                        running_prob = 0.45 + 0.5*(1 + running_neighbours)/(1 + len(neighbours))
                        if random.random() < running_prob:
                            path = [(reboot, 0), (v, 1)]
                            path.extend(utils.make_path(neighbours, bitmask))
                            paths.append(path)

                    if random.random() < self.inst_params['REBOOT-PROB']:
                        paths.append([(reboot, 0), (v, 0)])

                    self.paths_to_transition_constrs(paths, k, h, v)

    def get_instance_params(self):
        rddl_file = self.problem.file.replace('json', 'rddl')

        with open(rddl_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('computer'):
                    computers = utils.get_rddl_list(line)
                    self.inst_params['topology'] = {'running__%s' % computer: []
                                                    for computer in computers}
                elif line.startswith('REBOOT-PROB'):
                    self.inst_params['REBOOT-PROB'] = utils.get_rddl_assignment_val(line, float)
                elif line.startswith('REBOOT-PENALTY'):
                    self.inst_params['REBOOT-PENALTY'] = utils.get_rddl_assignment_val(line, float)
                elif line.startswith('CONNECTED'):
                    computers = utils.get_rddl_function_params(line, 'CONNECTED')
                    computers = ['running__%s' % c for c in computers]
                    self.inst_params['topology'][computers[1]].append(computers[0])

        logger.info('Read network parameters')

    def add_reward_objective(self):
        reboot_penalty = self.inst_params['REBOOT-PENALTY']

        for k in range(self.num_futures):
            for h in range(self.problem.horizon):
                for v in self.problem.variables:
                    a = self.find_matching_action(v)
                    paths = self.str_paths_to_var_paths(
                             [[(v, 0), (a, 0)], [(v, 0), (a, 1)], [(v, 1), (a, 0)], [(v, 1), (a, 1)]], k, h)
                    leaves = (0, -reboot_penalty, 1, 1 - reboot_penalty)

                    for i, (p, l) in enumerate(zip(paths, leaves)):
                        coeff = 1./self.num_futures * l
                        name = 'w^{}^{}^{}'.format(k, h, i)
                        w = self.model.addVar(vtype=GRB.BINARY, obj=coeff, name=name)
                        self.model.update()

                        constr_name = 'reward^{}^{}^{}'.format(k, h, i)
                        utils.add_and_constraints(self.model, p, w, name=constr_name)

        self.model.ModelSense = GRB.MAXIMIZE
        logger.info('added_reward_objective')

    @staticmethod
    def find_matching_action(state):
        return 'reboot%s' % (state[state.rindex('__'):],)
