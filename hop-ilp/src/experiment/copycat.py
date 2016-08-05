from base import Experiment
from logger import logger


class Copycat(Experiment):

    def start(self):
        actions, reward = self.solver.solve()

        logger.info('HOP Reward: {}'.format(reward))
        logger.info('Actions:\n{}'.format(actions))
