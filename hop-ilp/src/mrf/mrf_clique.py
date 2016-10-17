import math

# Potential function value for an invalid variables values assignment
INVALID_POTENTIAL_VAL = 0.00001


class MRFClique(object):

    def __init__(self, vars):
        self.vars = vars  # List of variables from least to most significant
        self.function_table = []

    def generate_states_function_table(self, determinized_tree, tree_vars):
        vars_values_gen = self.vars_values_generator(tree_vars)
        for vars_values in vars_values_gen:
            for expected_v in range(0, 2):
                curtree = determinized_tree
                while True:
                    if curtree is None:
                        if expected_v == 0:
                            self.function_table.append(1)
                        else:
                            self.function_table.append(INVALID_POTENTIAL_VAL)
                        break

                    if curtree.left is None and curtree.right is None:
                        if curtree.node.dvalue == expected_v:
                            self.function_table.append(1)
                        else:
                            self.function_table.append(INVALID_POTENTIAL_VAL)
                        break

                    if vars_values[curtree.node.name] == 1:
                        curtree = curtree.left
                    else:
                        curtree = curtree.right

    def generate_reward_function_table(self, reward_tree, tree_vars):
        vars_values_gen = self.vars_values_generator(tree_vars)
        for vars_values in vars_values_gen:
            reward = self.get_reward(vars_values, reward_tree)
            self.function_table.append(math.exp(reward))

    def get_reward(self, vars_values, reward_tree):
        """
        Recursively accumulates the rewards for a set of variable values along the reward tree
        """
        if reward_tree is None:
            return 0

        reward = 0.
        if reward_tree.node.name == 'branches':
            for subtree in reward_tree.node.value:
                reward += self.get_reward(vars_values, subtree)
            return reward

        if reward_tree.left is None and reward_tree.right is None:
            return reward_tree.node.value

        if vars_values[reward_tree.node.name] == 1:
            return self.get_reward(vars_values, reward_tree.left)
        return self.get_reward(vars_values, reward_tree.right)


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
