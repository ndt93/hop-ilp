import random
from logger import logger


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
                    self.determinize_paths(transition_trees[v], k, t, v)

    def determinize_paths(self, transition_tree, k, t, v):
        def determinize_path(nodes):
            if random.random() > nodes[-1][1]:
                self.mrf_model.add_states_clique(k, t, v, nodes, 0)
            else:
                self.mrf_model.add_states_clique(k, t, v, nodes, 1)

        transition_tree.traverse_paths(determinize_path, [])

    def build_reward_cliques(self):
        def build_reward_clique(nodes):
            for k in range(self.num_futures):
                for t in range(self.problem.horizon):
                    self.mrf_model.add_reward_clique(k, t, nodes)

        self.problem.reward_tree.traverse_paths(build_reward_clique, [])


class MRFModel(object):
    """
    MRF Model variables' indices order:
        states[future, time step],
        actions[future, time step],
        rewards[future, time step, path index]
    """
    vars_group_size = 0

    num_state_vars = 0
    num_action_vars = 0
    num_reward_vars = 0
    # Dict of variable names to local indices. These indices are locally
    # offset for each group of variables: states, actions. Rewards variables
    # indices are injected directly into the nodes of the reward tree
    vars_to_local_indices = {}

    cliques = []
    preamble = 'MARKOV'

    def __init__(self, num_futures, problem):
        self.vars_group_size = num_futures * problem.horizon
        self.map_vars_to_indices(problem)

    def add_states_clique(self, k, t, v, nodes, value):
        pass

    def add_reward_clique(self, k, t, nodes):
        pass

    def map_vars_to_indices(self, problem):
        self.num_state_vars = len(problem.variables)
        self.num_action_vars = len(problem.actions)

        for i, v in enumerate(problem.variables):
            self.vars_to_local_indices[v] = i
        for i, a in enumerate(problem.actions):
            self.vars_to_local_indices[a] = i
        self.map_reward_vars_indices(problem.reward_tree, 0)

    def map_reward_vars_indices(self, reward_tree, start_index):
        """
        Traverses the reward tree in order and inject incrementing indices
         to the leaves. This method also update the num_reward_vars field
         :param reward_tree
         :param start_index the smallest index in this tree
         :return the largest index for in this tree
        """
        if reward_tree.left is None and reward_tree.right is None:
            reward_tree.node.__dict__['index'] = start_index
            self.num_reward_vars += 1
            return start_index

        if reward_tree.left is not None:
            start_index = self.map_reward_vars_indices(reward_tree.left, start_index) + 1
        if reward_tree.right is not None:
            start_index = self.map_reward_vars_indices(reward_tree.right, start_index)

        return start_index

    def get_state_var_index(self, var_name, future, horizon):
        local_index = self.vars_to_local_indices[var_name]
        return local_index * self.vars_group_size + future * horizon + horizon

    def get_action_var_index(self, action_name, future, horizon):
        local_index = self.vars_to_local_indices[action_name]
        extended_local_index = local_index * self.vars_group_size + future * horizon + horizon
        return self.num_state_vars * self.vars_group_size + extended_local_index

    def get_global_reward_var_index(self, local_index, future, horizon):
        extended_local_index = local_index * self.vars_group_size + future * horizon + horizon
        # TODO: DRY
        return (self.num_state_vars + self.num_action_vars) * self.vars_group_size + extended_local_index

    def to_file(self, filename):
        # TODO: DRY
        num_state_action_vars = (self.num_state_vars + self.num_action_vars) * self.vars_group_size
        num_reward_vars = self.num_reward_vars * self.vars_group_size

        with open(filename, 'w') as f:
            write_line(f, self.preamble)
            write_line(f, num_state_action_vars + num_reward_vars)
            write_line(f, ' '.join(['2'] * num_state_action_vars + ['1'] * num_reward_vars))

            write_line(f, (len(self.cliques)))
            logger.info('write_model_to_file|f={}'.format(filename))


class MRFClique(object):
    vars = []
    function_table = []


def write_line(f, l):
    f.write('{}\n'.format(l))
