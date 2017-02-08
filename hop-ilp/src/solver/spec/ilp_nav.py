from gurobipy import *
from solver.spec.ilp_base import ILPBase
import utils
from logger import logger
import random
import re
import sys


class ILPNav(ILPBase):
    dir_to_action = {'NORTH': 'move_north', 'EAST': 'move_east',
                     'SOUTH': 'move_south', 'WEST': 'move_west'}
    opposite_action = {'move_north': 'move_south', 'move_south': 'move_north',
                       'move_east': 'move_west', 'move_west': 'move_east'}

    def __init__(self, *args, **kwargs):
        super(ILPNav, self).__init__(*args, **kwargs)
        self.inst_params = {
            'grid': {},
            'neighbours': {},
            'probs': {},
            'boundary': {},
            'goal': None,
        }
        self.get_instance_params()
        sys.exit(0)
        self.add_reward_objective()

    def set_transition_constrs(self):
        self.reset_transition_constrs()

        for k in range(self.num_futures):
            for h in range(1, self.problem.horizon):
                for v in self.problem.variables:
                    paths = []
                    self.paths_to_transition_constrs(paths, k, h, v)

        logger.info('set_transition_constrs')

    def add_reward_objective(self):
        goal = self.inst_params['goal']
        for k in range(self.num_futures):
            for h in range(self.problem.horizon):
                paths = self.str_paths_to_var_paths([[(goal, 0)], [goal, 1]], k, h)
                leaves = (-1, 0)
                self.paths_to_reward_constrs(paths, leaves, k, h)

        self.model.ModelSense = GRB.MAXIMIZE
        logger.info('added_reward_objective')

    def get_instance_params(self):
        rddl_file = self.problem.file.replace('json', 'rddl')
        with open(rddl_file, 'r') as f:
            for line in f:
                line = line.strip()

                if line.startswith('P'):
                    x, y = utils.get_rddl_function_params(line, 'P')
                    prob = utils.get_rddl_assignment_val(line, float)
                    self.inst_params['probs'][self.get_state_from_coords(x, y)] = prob
                    continue

                if line.startswith('GOAL'):
                    x, y = utils.get_rddl_function_params(line, 'GOAL')
                    self.inst_params['goal'] = self.get_state_from_coords(x, y)

                dir_match = re.match(r'(NORTH|EAST|SOUTH|WEST)', line)
                if dir_match:
                    dir = dir_match.group(1)
                    y, ny = utils.get_rddl_function_params(line, dir)
                    if y not in self.inst_params['grid']:
                        self.inst_params['grid'][y] = {}
                    self.inst_params['grid'][y][self.dir_to_action[dir]] = ny
                    continue

                boundary_match = re.match(r'(MIN-XPOS|MAX-XPOS|MIN-YPOS|MAX-YPOS)', line)
                if boundary_match:
                    terminal = boundary_match.group(1)
                    coord = utils.get_rddl_function_params(line, terminal)[0]
                    self.inst_params['boundary'][terminal] = coord

        self.inst_params['neighbours'] = self.grid_to_neighbours(self.inst_params['grid'])
        logger.info('loaded_instance_parameters')

    def grid_to_neighbours(self, grid):
        neighbours = {v: {} for v in self.problem.variables}
        for v in neighbours:
            x, y = self.get_coords_from_state(v)
            for a in grid[x]:
                neighbours[v][a] = self.get_state_from_coords(grid[x][a], y)
            for a in grid[y]:
                neighbours[v][a] = self.get_state_from_coords(x, grid[y][a])
        return neighbours

    @staticmethod
    def get_state_from_coords(x, y):
        return 'robot_at__%s_%s' % (x, y)

    @staticmethod
    def get_coords_from_state(state):
        coords_start = state.rindex('__')
        return state[coords_start + 2:].split('_')

