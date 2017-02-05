from logger import logger


class Model(object):
    variables = {}  # type: dict[str, int]
    actions = []  # type: list[str]
    transition_trees = {}
    reward_tree = None
    horizon = None  # type: int
    max_concurrency = None  # type: int
    file = ""

    def log_transition_trees(self):
        for v, t in self.transition_trees.items():
            logger.info('{}\n{!s}'.format(v, t))

    def log_reward_tree(self):
        logger.info('\n{}'.format(self.reward_tree))
