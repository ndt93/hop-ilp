class MRFClique(object):
    vars = []  # Variables (indices) from least to most significant
    function_table = []

    def __init__(self, vars):
        self.vars = vars

    def generate_states_function_table(self, determinized_tree, tree_vars, v):
        vars_values_gen = self.vars_values_generator(tree_vars)
        for vars_values in vars_values_gen:
            curtree = determinized_tree
            while True:
                if curtree is None:
                    self.function_table.append(1 - vars_values[v])
                    break

                if curtree.left is None and curtree.right is None:
                    if curtree.node.dvalue == vars_values[v]:
                        self.function_table.append(1)
                    else:
                        self.function_table.append(0)
                    break

                if vars_values[curtree.node.name] == 0:
                    curtree = curtree.left
                else:
                    curtree = curtree.right

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
