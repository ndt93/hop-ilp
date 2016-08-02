from copy import deepcopy
from tree import Node, Tree


def create_base_trees(variables):
    """
    Creates a Tree that represents all combinations of variables' values
    """

    if len(variables) == 0:
        return None

    subtree_actions = variables[1:]
    left_subtree = create_base_trees(subtree_actions)
    right_subtree = deepcopy(left_subtree)

    return Tree(Node(variables[0]), left_subtree, right_subtree)


def get_actions(action_block):
    """
    Get actions combination for an actionBlock AST

    :return: list of action names
    """

    actions_str = action_block.ID().getText()

    if actions_str == 'noop':
        return ()

    return actions_str.split('___')

