from gurobipy import *
from solver.spec.ilp_base import ILPBase
import utils
from logger import logger
import random


class ILPGol(ILPBase):

    def __init__(self, *args, **kwargs):
        super(ILPGol, self).__init__(*args, **kwargs)
        self.inst_params = {
            'neighbours': {},
            'NOISE-PROB': {},
        }
        self.get_instance_params()
        self.add_reward_objective()

    def set_transition_constrs(self):
        self.reset_transition_constrs()

        for k in range(self.num_futures):
            for h in range(1, self.problem.horizon):
                for v in self.problem.variables:
                    noise_prob = self.inst_params['NOISE-PROB'][v]
                    neighbours = self.inst_params['neighbours'][v]
                    set = self.find_matching_action(v)
                    paths = []

                    if random.random() < (1. - noise_prob):
                        paths.append([(set, 1)])

                    # Paths when cell v is alive
                    for bitmask in range(2**len(neighbours)):
                        set_neighbours = utils.count_set_bits(bitmask)
                        stay_alive = (2 <= set_neighbours <= 3) and (random.random() < 1.-noise_prob)
                        lucky = random.random() < noise_prob
                        if stay_alive or lucky:
                            path = [(set, 0), (v, 1)]
                            path.extend(utils.make_path(neighbours, bitmask))
                            paths.append(path)

                    # Paths when cell v is dead
                    for bitmask in range(2**len(neighbours)):
                        set_neighbours = utils.count_set_bits(bitmask)
                        born = (set_neighbours == 3) and (random.random() < 1.-noise_prob)
                        lucky = random.random() < noise_prob
                        if born or lucky:
                            path = [(set, 0), (v, 0)]
                            path.extend(utils.make_path(neighbours, bitmask))
                            paths.append(path)

                    self.paths_to_transition_constrs(paths, k, h, v)

        logger.info('set_transition_constrs')

    def add_reward_objective(self):
        for k in range(self.num_futures):
            for h in range(self.problem.horizon):
                for v in self.problem.variables:
                    a = self.find_matching_action(v)
                    paths = self.str_paths_to_var_paths(
                        [[(v, 0), (a, 0)], [(v, 0), (a, 1)], [(v, 1), (a, 0)], [(v, 1), (a, 1)]], k, h)
                    leaves = (0, -1, 1, 0)

                    for i, (p, l) in enumerate(zip(paths, leaves)):
                        coeff = 1./self.num_futures * l
                        name = 'w^{}^{}^{}'.format(k, h, i)
                        w = self.model.addVar(vtype=GRB.BINARY, obj=coeff, name=name)
                        self.model.update()

                        constr_name = 'reward^{}^{}^{}'.format(k, h, i)
                        utils.add_and_constraints(self.model, p, w, name=constr_name)

        self.model.ModelSense = GRB.MAXIMIZE
        logger.info('added_reward_objective')

    def get_instance_params(self):
        rddl_file = self.problem.file.replace('json', 'rddl')

        with open(rddl_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('NOISE-PROB'):
                    x, y = utils.get_rddl_function_params(line, 'NOISE-PROB')
                    val = utils.get_rddl_assignment_val(line, float)
                    self.inst_params['NOISE-PROB'][self.var_from_coord(x, y)] = val
                elif line.startswith('NEIGHBOR'):
                    x, y, nx, ny = utils.get_rddl_function_params(line, 'NEIGHBOR')
                    var = self.var_from_coord(x, y)
                    if var not in self.inst_params['neighbours']:
                        self.inst_params['neighbours'][var] = []
                    self.inst_params['neighbours'][var].append(self.var_from_coord(nx, ny))

        logger.info('loaded_instance_parameters')

    def get_noise_prob(self, cell):
        # type: (str) -> float
        return self.inst_params['NOISE-PROB'].get(cell, 0.1)

    @staticmethod
    def var_from_coord(x, y):
        return 'alive__%s_%s' % (x, y)

    @staticmethod
    def find_matching_action(state):
        return 'set%s' % (state[state.rindex('__'):],)
