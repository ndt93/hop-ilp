import random

from base import Experiment
from logger import logger


class Copycat(Experiment):
    """
    An experiment for the Copycat problem domain. State variables should
    have the x__{index} and y__{index} form. Action variables should have
    the a__{index} form in which the index is from the same set as the x states
    """

    num_steps = 0
    x_states = {}
    y_states = {}
    sorted_y_states = []

    def start(self):
        self.prompt()
        self.get_states()

        total_reward = 0
        for step in range(self.num_steps):
            actions, _ = self.solver.solve()
            self.log_results(step, actions)

            self.update_states(actions)
            reward = self.get_reward()
            total_reward += reward
            logger.info('{}. R: {}'.format(step, reward))

            all_states = dict(self.x_states.items(), **self.y_states)
            self.solver.init_next_step(all_states)

        logger.info('Total Reward: {}'.format(total_reward))

    def log_results(self, step, actions):
        x_states_str = Experiment.str_sorted_dict(self.x_states)
        y_states_str = Experiment.str_sorted_dict(self.y_states)
        actions_str = Experiment.str_sorted_dict(actions)

        logger.info('{}. X: {}'.format(step, x_states_str))
        logger.info('{}. Y: {}'.format(step, y_states_str))
        logger.info('{}. A: {}'.format(step, actions_str))

    def update_states(self, actions):
        is_matched = True
        for a in actions:
            index = a.split('__')[1]
            x_state = 'x__{}'.format(index)

            if actions[a] != self.x_states[x_state]:
                is_matched = False
                break

        if is_matched:
            i = 0
            sorted_ys = self.sorted_y_states
            while i < len(sorted_ys) and self.y_states[sorted_ys[i]] == 1:
                i += 1

            if i < len(sorted_ys):
                self.y_states[sorted_ys[i]] = 1

        for x in self.x_states:
            if random.random() < 0.5:
                self.x_states[x] = 0
            else:
                self.x_states[x] = 1

    def get_reward(self):
        return sum(self.y_states.values())

    def prompt(self):
        self.num_steps = int(input("Enter number of steps: "))

    def get_states(self):
        problem_vars = self.solver.problem.variables.items()
        self.x_states = {k: v for k, v in problem_vars if k.startswith('x')}
        self.y_states = {k: v for k, v in problem_vars if k.startswith('y')}
        self.sorted_y_states = sorted(self.y_states.keys())

