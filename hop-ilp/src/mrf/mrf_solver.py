import random
import subprocess
import os

from logger import logger
from mrf.mrf_model import MRFModel


class MRFSolver(object):
    MPLP_EXEC = './map_solver'
    OUTPUT_FILE = 'mrfmodel.uai'

    def __init__(self, name, problem, num_futures, time_limit=None, debug=False):
        logger.info('model_info|num_futures={},horizon={}'.format(num_futures, problem.horizon))
        self.num_futures = num_futures
        self.problem = problem
        self.time_limit = time_limit
        self.mrf_model = MRFModel(num_futures, problem)

    def solve(self):
        self.build_states_cliques()
        self.build_reward_cliques()
        self.build_init_conditions_cliques()
        self.mrf_model.to_file(self.OUTPUT_FILE)
        self.run_mplp()
        return self.get_next_actions()

    def get_next_actions(self):
        pass

    def run_mplp(self):
        logger.info('executing_mplp_solver|exec=%s' % self.MPLP_EXEC)
        mplp_env = os.environ.copy()
        mplp_env['INF_TIME'] = str(self.time_limit)

        mplp_proc = subprocess.Popen([self.MPLP_EXEC, self.OUTPUT_FILE],
                                     env=mplp_env, stdout=subprocess.PIPE)
        mplp_proc.wait()
        logger.info('execution_completed|returncode=%s' % mplp_proc.returncode)
        return mplp_proc.returncode

    def build_states_cliques(self):
        transition_trees = self.problem.transition_trees

        for k in range(self.num_futures):
            for t in range(self.problem.horizon - 1):
                for v in transition_trees:
                    transition_tree = transition_trees[v]
                    tree_vars = self.determinize_tree(transition_tree)
                    tree_vars.add(v)
                    self.mrf_model.add_states_clique(transition_tree, list(tree_vars), k, t, v)

        logger.info('added_states_cliques|cur_num_cliques={}'.format(len(self.mrf_model.cliques)))

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
        tree_vars = set()

        def collect_tree_vars(subtree):
            if subtree is None:
                return
            if subtree.node.name == 'branches':
                for branch in subtree.node.value:
                    collect_tree_vars(branch)
                return
            if subtree.left is None and subtree.right is None:
                return
            tree_vars.add(subtree.node.name)
            collect_tree_vars(subtree.left)
            collect_tree_vars(subtree.right)

        collect_tree_vars(self.problem.reward_tree)
        self.mrf_model.add_reward_cliques(self.problem.reward_tree, list(tree_vars))
        logger.info('added_reward_cliques|cur_num_cliques={}'.format(len(self.mrf_model.cliques)))

    def build_init_conditions_cliques(self):
        self.mrf_model.add_init_states_constrs_cliques()
        self.mrf_model.add_init_actions_constrs_cliques()
