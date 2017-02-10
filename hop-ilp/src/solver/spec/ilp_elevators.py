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

        for k in range(self.num_futures):
            for h in range(1, self.problem.horizon):
                for fl in self.inst_params['floors']:
                    self.set_person_waiting_transition_constr(fl, k, h)
                for el in self.inst_params['elevators']:
                    self.set_person_in_elevator_transition_constr(el, k, h)
                    self.set_elevator_closed_transition_constr(el, k, h)
                    self.set_elevator_dir_up_transition_constr(el, k, h)
                    for fl in self.inst_params['floors']:
                        self.set_elevator_at_floor_transition_constr(el, fl, k, h)

        logger.info('set_transition_constrs')

    def set_elevator_at_floor_transition_constr(self, el, fl, k, h):
        elevator_at_floor = self.get_elevator_at_state(el, fl)
        below_floor = self.inst_params['ADJACENT-DOWN'].get(fl)
        elevator_at_below_floor = self.get_elevator_at_state(el, below_floor)
        above_floor = self.inst_params['ADJACENT-UP'].get(fl)
        elevator_at_above_floor = self.get_elevator_at_state(el, above_floor)

        paths = [
            [(self.get_elevator_closed_state(el), 0), (elevator_at_floor, 1)],
            [(self.get_move_current_dir_action(el), 0), (elevator_at_floor, 1)],
        ]
        if elevator_at_below_floor is not None:
            paths.append([
                (self.get_move_current_dir_action(el), 1),
                (self.get_elevator_dir_up_state(el), 1),
                (self.get_elevator_at_state(el, below_floor), 1)
            ])
        else:
            paths.append([
                (self.get_move_current_dir_action(el), 1),
                (self.get_elevator_dir_up_state(el), 0),
                (elevator_at_floor, 1)
            ])
        if elevator_at_above_floor is not None:
            paths.append([
                (self.get_move_current_dir_action(el), 1),
                (self.get_elevator_dir_up_state(el), 0),
                (self.get_elevator_at_state(el, above_floor), 1)
            ])
        else:
            paths.append([
                (self.get_move_current_dir_action(el), 1),
                (self.get_elevator_dir_up_state(el), 1),
                (elevator_at_floor, 1)
            ])

    def set_elevator_dir_up_transition_constr(self, el, k, h):
        elevator_dir_up = self.get_elevator_dir_up_state(el)
        paths = [
            [(self.get_open_door_action(el, 'up'), 1)],
            [(self.get_open_door_action(el, 'down'), 0),
             (elevator_dir_up, 1)]
        ]
        self.paths_to_transition_constrs(paths, k, h, elevator_dir_up)

    def set_elevator_closed_transition_constr(self, el, k, h):
        elevator_closed = self.get_elevator_closed_state(el)
        paths = [
            [(self.get_close_door_action(el), 1)],
            [(elevator_closed, 1),
             (self.get_open_door_action(el, 'up'), 0),
             (self.get_open_door_action(el, 'down'), 0)],
        ]
        self.paths_to_transition_constrs(paths, k, h, elevator_closed)

    def set_person_in_elevator_transition_constr(self, el, k, h):
        person_going_up = self.get_person_in_elevator_state(el, 'up')
        elevator_at_top_floor = self.get_elevator_at_state(el, self.inst_params['TOP-FLOOR'])
        paths = [[(person_going_up, 1), (elevator_at_top_floor, 0)]]
        paths.extend([
            [(person_going_up, 0),
             (self.get_elevator_at_state(el, fl), 1),
             (self.get_elevator_dir_up_state(el), 1),
             (self.get_elevator_closed_state(el), 0),
             (self.get_person_waiting_state(fl, 'up'), 1)]
            for fl in self.inst_params['floors']
        ])
        self.paths_to_transition_constrs(paths, k, h, person_going_up)

        person_going_down = self.get_person_in_elevator_state(el, 'down')
        elevator_at_bottom_floor = self.get_elevator_at_state(el, self.inst_params['BOTTOM-FLOOR'])
        paths = [[(person_going_down, 1), (elevator_at_bottom_floor, 0)]]
        paths.extend([
             [(person_going_down, 0),
              (self.get_elevator_at_state(el, fl), 1),
              (self.get_elevator_dir_up_state(el), 0),
              (self.get_elevator_closed_state(el), 0),
              (self.get_person_waiting_state(fl, 'down'), 1)]
             for fl in self.inst_params['floors']
        ])
        self.paths_to_transition_constrs(paths, k, h, person_going_down)

    def set_person_waiting_transition_constr(self, fl, k, h):
        person_waiting_up = self.get_person_waiting_state(fl, 'up')
        paths = []
        if random.random() >= self.get_arrive_prob(fl):
            paths.append([(person_waiting_up, 0)])
        paths.extend([[(person_waiting_up, 1),
                       (self.get_elevator_at_state(el, fl), 1),
                       (self.get_elevator_dir_up_state(el), 1),
                       (self.get_elevator_closed_state(el), 0)]
                      for el in self.inst_params['elevators']])
        self.paths_to_transition_constrs(paths, k, h, person_waiting_up, paths_val=0)

        person_waiting_down = self.get_person_waiting_state(fl, 'down')
        paths = []
        if random.random() >= self.get_arrive_prob(fl):
            paths.append([(person_waiting_down, 0)])
        paths.extend([[(person_waiting_down, 1),
                       (self.get_elevator_at_state(el, fl), 1),
                       (self.get_elevator_dir_up_state(el), 0),
                       (self.get_elevator_closed_state(el), 0)]
                      for el in self.inst_params['elevators']])
        self.paths_to_transition_constrs(paths, k, h, person_waiting_down, paths_val=0)

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
                self.paths_to_reward_constrs(self.str_paths_to_var_paths(paths, k, h),
                                             leaves, k, h)

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
                    self.inst_params['TOP-FLOOR'] = utils.get_rddl_function_params(line, 'TOP-FLOOR')[0]
                elif line.startswith('BOTTOM-FLOOR'):
                    self.inst_params['BOTTOM-FLOOR'] = utils.get_rddl_function_params(line, 'BOTTOM-FLOOR')[0]
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
