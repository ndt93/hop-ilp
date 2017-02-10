from gurobipy import *
from solver.spec.ilp_base import ILPBase
import utils
from logger import logger
import random
import re


class ILPElevators(ILPBase):

    def __init__(self, *args, **kwargs):
        super(ILPElevators, self).__init__(*args, **kwargs)
        self.inst_params = {
            'elevators': [],
            'floors': [],
            'arrive_probs': {},
            'ELEVATOR-PENALTY-RIGHT-DIR': 0.75,
            'ELEVATOR-PENALTY-WRONG-DIR': 3.0,
            'DEFAULT-ARRIVE-PROB': 0.0,
            'TOP-FLOOR': '',
            'BOTTOM-FLOOR': '',
            'ADJACENT-UP': {},
            'ADJACENT-DOWN': {}
        }
        self.get_instance_params()
        self.add_reward_objective()

    def set_transition_constrs(self):
        self.reset_transition_constrs()
        goal = self.inst_params['goal']

        for k in range(self.num_futures):
            for h in range(1, self.problem.horizon):
                for v in self.problem.variables:
                    neighbours = self.inst_params['neighbours'][v]
                    paths = []

                    if v == goal:
                        paths.append([(goal, 1)])

                    for a in neighbours:
                        path = [(goal, 0)] if v != goal else []
                        if random.random() < 1. - self.get_disappear_prob(v):
                            path.extend([(self.opposite_action[a], 1), (neighbours[a], 1)])
                        if len(path) > 0:
                            paths.append(path)

                    if v != goal:
                        path = [(goal, 0), (v, 1)] + [(a, 0) for a in neighbours]
                        paths.append(path)

                    self.paths_to_transition_constrs(paths, k, h, v)

        logger.info('set_transition_constrs')

    def add_reward_objective(self):
        for k in range(self.num_futures):
            for h in range(self.problem.horizon):
                paths = []
                leaves = []
                for el in self.inst_params['elevators']:
                    person_going_up = self.get_person_in_elevator_state(el, 'up')
                    person_going_down = self.get_person_in_elevator_state(el, 'down')
                    elevator_dir_up = self.get_elevator_dir_up_state(el)
                    paths.extend([
                        [(elevator_dir_up, 1), (person_going_up, 1)],
                        [(elevator_dir_up, 0), (person_going_down, 1)],
                        [(elevator_dir_up, 0), (person_going_up, 1)],
                        [(elevator_dir_up, 1), (person_going_down, 1)]
                    ])
                    leaves.extend([-self.inst_params['ELEVATOR-PENALTY-RIGHT-DIR'],
                                   -self.inst_params['ELEVATOR-PENALTY-RIGHT-DIR'],
                                   -self.inst_params['ELEVATOR-PENALTY-WRONG-DIR'],
                                   -self.inst_params['ELEVATOR-PENALTY-WRONG-DIR']])
                for fl in self.inst_params['floors']:
                    person_waiting_up = self.get_person_waiting_state(fl, 'up')
                    person_waiting_down = self.get_person_waiting_state(fl, 'down')
                    paths.extend([
                        [(person_waiting_up, 0), (person_waiting_down, 0)],
                        [(person_waiting_up, 0), (person_waiting_down, 1)],
                        [(person_waiting_up, 1), (person_waiting_down, 0)],
                        [(person_waiting_up, 1), (person_waiting_down, 1)],
                    ])
                    leaves.extend([0, -1, -1, -2])
                self.paths_to_reward_constrs(paths, leaves, k, h)

        self.model.ModelSense = GRB.MAXIMIZE
        logger.info('added_reward_objective')

    def get_instance_params(self):
        rddl_file = self.problem.file.replace('json', 'rddl')
        with open(rddl_file, 'r') as f:
            for line in f:
                line = line.strip()
                if re.match(r'elevator\s*:', line):
                    self.inst_params['elevators'] = utils.get_rddl_list(line)
                elif line.startswith('floor'):
                    self.inst_params['floors'] = utils.get_rddl_list(line)
                elif line.startswith('ELEVATOR-PENALTY-RIGHT-DIR'):
                    self.inst_params['ELEVATOR-PENALTY-RIGHT-DIR'] = \
                        utils.get_rddl_assignment_val(line, float)
                elif line.startswith('ELEVATOR-PENALTY-WRONG-DIR'):
                    self.inst_params['ELEVATOR-PENALTY-WRONG-DIR'] = \
                        utils.get_rddl_assignment_val(line, float)
                elif line.startswith('ARRIVE-PARAM'):
                    floor = utils.get_rddl_function_params(line, 'ARRIVE-PARAM')[0]
                    prob = utils.get_rddl_assignment_val(line, float)
                    self.inst_params['arrive_probs'][floor] = prob
                elif line.startswith('TOP-FLOOR'):
                    top_floor = utils.get_rddl_function_params(line, 'TOP-FLOOR')[0]
                    for i, floor in enumerate(self.inst_params['floors']):
                        if floor == top_floor:
                            self.inst_params['TOP-FLOOR'] = i
                            break
                elif line.startswith('BOTTOM-FLOOR'):
                    bottom_floor = utils.get_rddl_function_params(line, 'BOTTOM-FLOOR')[0]
                    for i, floor in enumerate(self.inst_params['floors']):
                        if floor == bottom_floor:
                            self.inst_params['BOTTOM-FLOOR'] = i
                            break
                elif line.startswith('ADJACENT-UP'):
                    lower_floor, upper_floor = utils.get_rddl_function_params(line, 'ADJACENT-UP')
                    self.inst_params['ADJACENT-UP'][lower_floor] = upper_floor
                    self.inst_params['ADJACENT-DOWN'][upper_floor] = lower_floor

    def get_arrive_prob(self, floor):
        return self.inst_params['arrive_probs'].get(floor, self.inst_params['DEFAULT-ARRIVE-PROB'])

    @staticmethod
    def get_elevator_dir_up_state(elevator):
        return 'elevator_dir_up__%s' % (elevator,)

    @staticmethod
    def get_person_in_elevator_state(elevator, direction):
        return 'person_in_elevator_going_%s__%s' % (direction, elevator)

    @staticmethod
    def get_person_waiting_state(floor, direction):
        return 'person_waiting_%s__%s' % (direction, floor)

    @staticmethod
    def get_elevator_at_state(elevator, floor):
        return 'elevator_at_floor__%s_%s' % (elevator, floor)

    @staticmethod
    def get_elevator_closed_state(elevator):
        return 'elevator_closed__%s' % (elevator,)

    @staticmethod
    def get_open_door_action(elevator, direction):
        return 'open_door_going_%s__%s' % (direction, elevator)

    @staticmethod
    def get_close_door_action(elevator):
        return 'close_door__%s' % (elevator,)

    @staticmethod
    def get_move_current_dir_action(elevator):
        return 'move_current_dir__%s' % (elevator,)
