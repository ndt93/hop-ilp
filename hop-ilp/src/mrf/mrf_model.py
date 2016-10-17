from logger import logger
from mrf.mrf_clique import MRFClique, INVALID_POTENTIAL_VAL


class MRFModel(object):
    """
    MRF Model variables' indices order:
        states[future, time step],
        actions[future, time step],
        rewards[future, time step]
    """
    vars_group_size = 0

    # Number of variables, ignoring future and horizon
    num_mdp_state_vars = 0
    num_mdp_action_vars = 0
    # Number of variables, considering future and horizon
    num_mrf_state_vars = 0  # Both MDP states and actions are MRF states
    num_mrf_reward_vars = 0
    # Dict of variable names to local indices. These indices are locally
    # offset for each group of variables: states, actions.
    vars_local_indices = {}
    # Variables (states and actions) local indices to variable names
    local_indices_to_vars = {}

    cliques = []
    preamble = 'MARKOV'

    def __init__(self, num_futures, problem):
        self.num_futures = num_futures
        self.problem = problem

        self.num_mdp_state_vars = len(problem.variables)
        self.num_mdp_action_vars = len(problem.actions)

        self.vars_group_size = num_futures * problem.horizon
        self.num_mrf_state_vars = (self.num_mdp_state_vars + self.num_mdp_action_vars) * self.vars_group_size
        self.num_mrf_reward_vars = self.vars_group_size

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
        var_indices = [self.get_state_var_index(v, k, t + 1)]
        var_indices.extend(self.state_vars_to_indices(tree_vars, k, t))
        clique = MRFClique(var_indices)
        clique.generate_states_function_table(determinized_tree, tree_vars)
        self.cliques.append(clique)
        # print('--- Future %d Horizon %d ---' % (k, t))
        # self.print_clique(clique)

    def add_reward_cliques(self, reward_tree, tree_vars):
        assert(self.num_futures > 0 and self.problem.horizon > 0)
        var_indices = self.state_vars_to_indices(tree_vars, 0, 0)
        var_indices.append(self.get_reward_var_index(0, 0))
        clique_proto = MRFClique(var_indices)
        clique_proto.generate_reward_function_table(reward_tree, tree_vars)
        self.cliques.append(clique_proto)

        for k in range(self.num_futures):
            for t in range(self.problem.horizon):
                if k == 0 and t == 0:
                    continue
                var_indices = self.state_vars_to_indices(tree_vars, k, t)
                var_indices.append(self.get_reward_var_index(k, t))
                clique = MRFClique(var_indices)
                clique.function_table = clique_proto.function_table
                self.cliques.append(clique)

    def add_init_states_constrs_cliques(self):
        vars_list = list(self.problem.variables)
        vars_vals_bitset = 0
        for i, v in enumerate(vars_list):
            vars_vals_bitset |= (int(self.problem.variables[v]) << i)

        for k in range(self.num_futures):
            vars_indices = self.state_vars_to_indices(vars_list, k, 0)
            clique = MRFClique(vars_indices)
            for i in range(2**len(vars_list)):
                if i == vars_vals_bitset:
                    clique.function_table.append(1)
                else:
                    clique.function_table.append(INVALID_POTENTIAL_VAL)

            self.cliques.append(clique)
        logger.info('added_init_states_cliques|cur_num_cliques={}'.format(len(self.cliques)))

    def add_init_actions_constrs_cliques(self):
        function_table = []
        allset = 2**self.num_futures - 1
        for i in range(2**self.num_futures):
            if i == 0 or i == allset:
                function_table.append(1)
            else:
                function_table.append(INVALID_POTENTIAL_VAL)

        for action in self.problem.actions:
            vars_indices = [self.get_state_var_index(action, k, 0) for k in range(self.num_futures)]
            clique = MRFClique(vars_indices)
            clique.function_table = function_table
            self.cliques.append(clique)
        logger.info('added_init_actions_cliques|cur_num_cliques={}'.format(len(self.cliques)))

    def state_vars_to_indices(self, vars, k, t):
        return [self.get_state_var_index(var, k, t) for var in vars]

    def map_vars_to_indices(self, problem):
        for i, v in enumerate(problem.variables):
            self.vars_local_indices[v] = i
            self.local_indices_to_vars[i] = v
        for i, a in enumerate(problem.actions):
            self.vars_local_indices[a] = i + self.num_mdp_state_vars
            self.local_indices_to_vars[i + self.num_mdp_state_vars] = a
        logger.info('mapped_variables_to_indices|mapping=\n{}'.format(self.vars_local_indices))

    def get_state_var_index(self, var_name, future, horizon):
        local_index = self.vars_local_indices[var_name]
        return local_index*self.vars_group_size + future*self.problem.horizon + horizon

    def get_reward_var_index(self, future, horizon):
        local_index = future * self.problem.horizon + horizon
        return self.num_mrf_state_vars + local_index

    def get_state_from_index(self, index):
        """
        Returns (variable name, future, horizon) from global index
        """
        local_index = index / self.vars_group_size
        future = (index % self.vars_group_size) / self.problem.horizon
        horizon = (index % self.vars_group_size) % self.problem.horizon
        return self.local_indices_to_vars[local_index], future, horizon

    def to_file(self, filename):
        with open(filename, 'w') as f:
            write_line(f, self.preamble)
            write_line(f, self.num_mrf_state_vars + self.num_mrf_reward_vars)
            write_line(f, ' '.join(['2'] * self.num_mrf_state_vars + ['1'] * self.num_mrf_reward_vars))

            write_line(f, (len(self.cliques)))
            for clique in self.cliques:
                f.write('{} {}\n'.format(len(clique.vars),
                                         ' '.join(stringify(clique.vars[::-1]))))
            for clique in self.cliques:
                f.write('{}\n{}\n'.format(len(clique.function_table),
                                          ' '.join(stringify(clique.function_table))))

            logger.info('write_model_to_file|f={}'.format(filename))

    def print_clique(self, clique):
        mdp_vars = [str(self.get_state_from_index(i)) for i in clique.vars]
        print(','.join(mdp_vars[::-1]))
        for i, v in enumerate(clique.function_table):
            print('{i:0{width}b}: {v}'.format(i=i, v=v, width=len(mdp_vars)))


def stringify(l):
    return [str(x) for x in l]


def write_line(f, l):
    f.write('{}\n'.format(l))
