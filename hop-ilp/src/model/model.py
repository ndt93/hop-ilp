from logger import logger


class Model(object):
    variables = {}
    actions = []
    transition_trees = {}
    reward_tree = None
    horizon = None
    max_concurrency = None
    file = ""

    def log_transition_trees(self):
        for v, t in self.transition_trees.items():
            logger.info('{}\n{!s}'.format(v, t))

    def log_reward_tree(self):
        logger.info('\n{}'.format(self.reward_tree))
