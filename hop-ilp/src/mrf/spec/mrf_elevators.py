from logger import logger
import mrf
from mrf.spec.mrf_base import BaseMRF
from mrf.mrf_clique import MRFClique
import mrf.utils as utils
import random
import math
import re
import itertools


class ElevatorsMRF(BaseMRF):
    inst_params = {
        'elevators': [],
        'floors': [],
        'arrive_probs': {},
        'ELEVATOR-PENALTY-RIGHT-DIR': 0.75,
        'ELEVATOR-PENALTY-WRONG-DIR': 3.0,
        'DEFAULT-ARRIVE-PROB': 0.0,
        'TOP-FLOOR': '',
        'BOTTOM-FLOOR': '',
    }

    def __init__(self, *args, **kwargs):
        BaseMRF.__init__(self, *args, **kwargs)
        self.get_instance_params()
        self.add_fixed_constrs(concurrency=True)
        if self.debug:
            logger.debug(self.problem.variables)
            logger.debug(self.problem.actions)
            logger.debug(self.inst_params)

    def solve(self):
        self.set_init_states_constrs(self.problem.variables)
        self.set_transition_constrs()

        #self.write_mrf(mrf.OUTPUT_FILE)
        #map_assignments = self.mplp_runner.run_mplp()
        #next_actions = self.mplp_runner.get_next_actions(map_assignments)

        #logger.info('next_action|states={},actions={}'.format(self.problem.variables, next_actions))
        #return next_actions, None

    def init_next_step(self, states):
        self.problem.variables.update(states)

    def set_transition_constrs(self):
        self.constrs['transition'] = []

        for k in range(self.num_futures):
            for h in range(1, self.problem.horizon):
                self.set_person_waiting_transition(k, h)
                self.set_person_in_elevator_transition(k, h)
                self.set_elevator_closed_transition(k, h)
                self.set_elevator_dir_up_transition(k, h)
        logger.info('set_transition_constraints')

    def set_elevator_dir_up_transition(self, k, h):
        for elevator in self.inst_params['elevators']:
            var_indices = [self.get_elevator_dir_state(elevator, 'up'),
                           self.get_elevator_dir_state(elevator, 'up'),
                           self.get_open_door_action(elevator, 'up'),
                           self.get_open_door_action(elevator, 'down')]
            clique = MRFClique(var_indices)
            for bitmask in range(2**len(var_indices)):
                if utils.is_set(bitmask, 2):
                    utils.append_function_entry(clique, bitmask, 0, 1)
                    continue

                if utils.is_set(bitmask, 3):
                    utils.append_function_entry(clique, bitmask, 0, 0)
                    continue

                val = 1 if utils.is_set(bitmask, 1) else 0
                utils.append_function_entry(clique, bitmask, 0, val)

    def set_elevator_closed_transition(self, k, h):
        for elevator in self.inst_params['elevators']:
            var_indices = [self.get_elevator_closed_state(elevator),
                           self.get_elevator_closed_state(elevator),
                           self.get_open_door_action(elevator, 'up'),
                           self.get_open_door_action(elevator, 'down'),
                           self.get_close_door_action(elevator)]
            var_indices[0] = self.var_to_idx[(var_indices[0], k, h)]
            var_indices[1:] = [self.var_to_idx[(v, k, h - 1)] for v in var_indices[1:]]

            clique = MRFClique(var_indices)
            for bitmask in range(2**len(var_indices)):
                if utils.is_set(bitmask, 1) and not utils.is_set(bitmask, 2) \
                        and not utils.is_set(bitmask, 3) and utils.is_set(bitmask, 4):
                    utils.append_function_entry(clique, bitmask, 0, 1)
                else:
                    utils.append_function_entry(clique, bitmask, 0, 0)
            self.constrs['transition'].append(clique)

    def set_person_in_elevator_transition(self, k, h):
        for elevator in self.inst_params['elevators']:
            person_in_elevator_going_up = self.get_person_in_elevator_state(elevator, 'up')
            person_in_elevator_going_down = self.get_person_in_elevator_state(elevator, 'down')
            elevator_closed = self.get_elevator_closed_state(elevator)
            elevator_dir_up = self.get_elevator_dir_state(elevator, 'up')
            elevator_at_floor = [self.get_elevator_at_state(elevator, floor)
                                 for floor in self.inst_params['floors']]
            person_waiting_up = [self.get_person_waiting_state(floor, 'up')
                                 for floor in self.inst_params['floors']]
            person_waiting_down = [self.get_person_waiting_state(floor, 'down')
                                   for floor in self.inst_params['floors']]

            floor_offset = 4
            waiting_offset = floor_offset + len(elevator_at_floor)
            common_indices = [(elevator_closed, k, h - 1), (elevator_dir_up, k, h - 1)]
            common_indices += [(v, k, h - 1) for v in elevator_at_floor]

            # Going up
            var_indices = [(person_in_elevator_going_up, k, h), (person_in_elevator_going_up, k, h - 1)]
            var_indices += common_indices + [(v, k, h - 1) for v in person_waiting_up]
            var_indices = [self.var_to_idx[v] for v in var_indices]
            elevator_at_top_floor_idx = 4 + self.inst_params['TOP-FLOOR']
            clique = MRFClique(var_indices)
            for bitmask in range(2**len(var_indices)):
                if utils.is_set(bitmask, 1):
                    if utils.is_set(bitmask, elevator_at_top_floor_idx):
                        utils.append_function_entry(clique, bitmask, 0, 0)
                    else:
                        utils.append_function_entry(clique, bitmask, 0, 1)
                    continue

                if utils.is_set(bitmask, 2):
                    utils.append_function_entry(clique, bitmask, 0, 0)
                    continue

                if not utils.is_set(bitmask, 3):
                    utils.append_function_entry(clique, bitmask, 0, 0)
                    continue

                done = False
                for i in range(len(elevator_at_floor)):
                    if utils.is_set(bitmask, floor_offset + i) and utils.is_set(bitmask, waiting_offset + i):
                        utils.append_function_entry(clique, bitmask, 0, 1)
                        done = True
                        break
                if not done:
                    utils.append_function_entry(clique, bitmask, 0, 0)
            self.constrs['transition'].append(clique)

            # Going down
            var_indices = [(person_in_elevator_going_down, k, h), (person_in_elevator_going_down, k, h - 1)]
            var_indices += common_indices + [(v, k, h - 1) for v in person_waiting_down]
            var_indices = [self.var_to_idx[v] for v in var_indices]
            elevator_at_bottom_floor_idx = 4 + self.inst_params['BOTTOM-FLOOR']
            clique = MRFClique(var_indices)
            for bitmask in range(2**len(var_indices)):
                if utils.is_set(bitmask, 1):
                    if utils.is_set(bitmask, elevator_at_bottom_floor_idx):
                        utils.append_function_entry(clique, bitmask, 0, 0)
                    else:
                        utils.append_function_entry(clique, bitmask, 0, 1)
                    continue

                if utils.is_set(bitmask, 2):
                    utils.append_function_entry(clique, bitmask, 0, 0)
                    continue

                if utils.is_set(bitmask, 3):
                    utils.append_function_entry(clique, bitmask, 0, 0)
                    continue

                done = False
                for i in range(len(elevator_at_floor)):
                    if utils.is_set(bitmask, floor_offset + i) and utils.is_set(bitmask, waiting_offset + i):
                        utils.append_function_entry(clique, bitmask, 0, 1)
                        done = True
                        break
                if not done:
                    utils.append_function_entry(clique, bitmask, 0, 0)

    def set_person_waiting_transition(self, k, h):
        for floor in self.inst_params['floors']:
            person_waiting_up = self.get_person_waiting_state(floor, 'up')
            elevator_states = [(self.get_elevator_at_state(e, floor),
                                self.get_elevator_dir_state(e, 'up'),
                                self.get_elevator_closed_state(e))
                               for e in self.inst_params['elevators']]
            var_indices = [self.var_to_idx[(person_waiting_up, k, h)],
                           self.var_to_idx[(person_waiting_up, k, h-1)]]
            var_indices += [self.var_to_idx[(es, k, h-1)] for es in itertools.chain(*elevator_states)]
            clique = MRFClique(var_indices)
            for bitmask in range(2**len(var_indices)):
                is_elevator_available = False
                for i in range(len(elevator_states)):
                    if (utils.is_set(bitmask, 2+i*3)
                            and utils.is_set(bitmask, 3+i*3)
                            and not utils.is_set(bitmask, 4+i*3)):
                        is_elevator_available = True
                if utils.is_set(bitmask, 1) and not is_elevator_available:
                    if utils.is_set(bitmask, 0):
                        clique.function_table.append(1)
                    else:
                        clique.function_table.append(mrf.INVALID_POTENTIAL_VAL)
                else:
                    determinized_val = 0
                    if random.random() < self.get_arrive_prob(floor):
                        determinized_val = 1

                    if utils.match_determinized_val(bitmask, 0, determinized_val):
                        clique.function_table.append(1)
                    else:
                        clique.function_table.append(mrf.INVALID_POTENTIAL_VAL)
            self.constrs['transition'].append(clique)

    def add_reward_constrs(self):
        right_dir_penalty = self.inst_params['ELEVATOR-PENALTY-RIGHT-DIR']
        wrong_dir_penalty = self.inst_params['ELEVATOR-PENALTY-WRONG-DIR']
        for k in range(self.num_futures):
            for h in range(self.problem.horizon):
                for elevator in self.inst_params['elevators']:
                    elevator_dir_up = self.get_elevator_dir_state(elevator, 'up')
                    person_going_up = self.get_person_in_elevator_state(elevator, 'up')
                    person_going_down = self.get_person_in_elevator_state(elevator, 'down')

                    clique = MRFClique([self.var_to_idx[(elevator_dir_up, k, h)],
                                        self.var_to_idx[(person_going_up, k, h)]])
                    clique.function_table = [1, 1,
                                             math.exp(-wrong_dir_penalty), math.exp(-right_dir_penalty)]
                    self.constrs['reward'].append(clique)

                    clique = MRFClique([self.var_to_idx[(elevator_dir_up, k, h)],
                                        self.var_to_idx[(person_going_down, k, h)]])
                    clique.function_table = [1, 1,
                                             math.exp(-right_dir_penalty), math.exp(-wrong_dir_penalty)]
                    self.constrs['reward'].append(clique)
        logger.info('Added reward constraints')

    def get_instance_params(self):
        rddl_file = self.problem.file.replace('json', 'rddl')
        with open(rddl_file, 'r') as f:
            for line in f:
                line = line.strip()
                if re.match(r'elevator\s*:', line):
                    self.inst_params['elevators'] = self.get_rddl_list(line)
                elif line.startswith('floor'):
                    self.inst_params['floors'] = self.get_rddl_list(line)
                elif line.startswith('ELEVATOR-PENALTY-RIGHT-DIR'):
                    self.inst_params['ELEVATOR-PENALTY-RIGHT-DIR'] =\
                        self.get_rddl_assignment_val(line, float)
                elif line.startswith('ELEVATOR-PENALTY-WRONG-DIR'):
                    self.inst_params['ELEVATOR-PENALTY-WRONG-DIR'] =\
                        self.get_rddl_assignment_val(line, float)
                elif line.startswith('ARRIVE-PARAM'):
                    floor = self.get_rddl_function_params(line, 'ARRIVE-PARAM')[0]
                    prob = self.get_rddl_assignment_val(line, float)
                    self.inst_params['arrive_probs'][floor] = prob
                elif line.startswith('TOP-FLOOR'):
                    top_floor = self.get_rddl_function_params(line, 'TOP-FLOOR')[0]
                    for i, floor in enumerate(self.inst_params['floors']):
                        if floor == top_floor:
                            self.inst_params['TOP-FLOOR'] = i
                            break
                elif line.startswith('BOTTOM-FLOOR'):
                    bottom_floor = self.get_rddl_function_params(line, 'BOTTOM-FLOOR')[0]
                    for i, floor in enumerate(self.inst_params['floors']):
                        if floor == bottom_floor:
                            self.inst_params['BOTTOM-FLOOR'] = i
                            break

    def get_arrive_prob(self, floor):
        return self.inst_params['arrive_probs'].get(floor, self.inst_params['DEFAULT-ARRIVE-PROB'])

    @staticmethod
    def get_rddl_list(line):
        list_str = line[line.index('{')+1:line.rindex('}')]
        return re.split(r'\W+', list_str.strip())

    @staticmethod
    def get_elevator_dir_state(elevator, direction):
        return 'elevator_dir_%s__%s' % (direction, elevator)

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
