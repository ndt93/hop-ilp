import random

from logger import logger
from mrf.mrf_model import MRFModel


class MRFSolver(object):
    def __init__(self, name, problem, num_futures, time_limit=None, debug=False):
        logger.info('model_info|num_futures={},horizon={}'.format(num_futures, problem.horizon))
        self.num_futures = num_futures
        self.problem = problem
        self.mrf_model = MRFModel(num_futures, problem)

    def solve(self):
        self.build_states_cliques()
        self.build_reward_cliques()
        self.mrf_model.to_file('mrfmodel.txt')

    def build_states_cliques(self):
        transition_trees = self.problem.transition_trees

        for k in range(self.num_futures):
            for t in range(self.problem.horizon - 1):
                for v in transition_trees:
                    transition_tree = transition_trees[v]
                    tree_vars = self.determinize_tree(transition_tree)
                    tree_vars.add(v)
                    self.mrf_model.add_states_clique(transition_tree, list(tree_vars), k, t, v)

    def determinize_tree(self, transition_tree):
        """
        Determinizes a transition tree and returns the list of all variables in the tree.
        The determinized value will be injected to the leaf node as the `dvalue` attribute.
        """
        vars_in_tree = set()

        def determinize_subtree(subtree):
            if subtree.left is None and subtree.right is None:
                if random.random() > subtree.node.value:
                    subtree.node.__dict__['dvalue'] = 0
                else:
                    subtree.node.__dict__['dvalue'] = 1
                return

            vars_in_tree.add(subtree.node.name)
            if subtree.left is not None:
                determinize_subtree(subtree.left)
            if subtree.right is not None:
                determinize_subtree(subtree.right)

        determinize_subtree(transition_tree)
        return vars_in_tree

    def build_reward_cliques(self):
        pass
