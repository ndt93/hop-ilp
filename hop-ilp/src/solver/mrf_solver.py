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

    def add_states_clique(self, determinized_tree, tree_vars, k, t, v):
        var_indices = [self.get_state_var_index(var, k, t) for var in tree_vars]
        clique = MRFClique(var_indices)
        clique.generate_states_function_table(determinized_tree, tree_vars, v)
        self.cliques.append(clique)

    def map_vars_to_indices(self, problem):
        self.num_state_vars = len(problem.variables)
        self.num_action_vars = len(problem.actions)

        for i, v in enumerate(problem.variables):
            self.vars_to_local_indices[v] = i
        for i, a in enumerate(problem.actions):
            self.vars_to_local_indices[a] = i + self.num_state_vars
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

    def __init__(self, vars):
        self.vars = vars

    def generate_states_function_table(self, determinized_tree, tree_vars, v):
        vars_values_gen = self.vars_values_generator(tree_vars)
        for vars_values in vars_values_gen:
            print(vars_values)

    @staticmethod
    def vars_values_generator(tree_vars):
        result = {}
        vals = 0
        end = 2**len(tree_vars)

        while vals < end:
            for i in range(len(tree_vars)):
                if vals & (1 << i) > 0:
                    result[tree_vars[i]] = 1
                else:
                    result[tree_vars[i]] = 0

            yield result
            vals += 1



def write_line(f, l):
    f.write('{}\n'.format(l))
