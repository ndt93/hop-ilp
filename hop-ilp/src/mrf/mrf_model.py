from logger import logger
from mrf.mrf_clique import MRFClique


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
        """
        Adds a clique i.e. a potential function that represents a determinized transition tree.
        The function maps to 1 or 0 whether the values assigned to the variables in the tree
        satisfies the determinized value or not respectively
        :param determinized_tree: a determinized transition tree
        :param tree_vars: all variables in the transition tree
        :param k: the future value
        :param t: the horizon step
        :param v: name of state variable to make the transition to
        """
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
            for clique in self.cliques:
                write_line(f, ' '.join(stringify(clique.vars[::-1])))
                write_line(f, ' '.join(stringify(clique.function_table)))

            logger.info('write_model_to_file|f={}'.format(filename))


def stringify(l):
    return [str(x) for x in l]


def write_line(f, l):
    f.write('{}\n'.format(l))
