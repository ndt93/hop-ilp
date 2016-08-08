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


def create_dtree(dtree, leaf_transform=None):
    """
    Creates a decision tree from a dtree AST
    """

    if dtree.left is None and dtree.right is None:
        val = float(dtree.node().number().getText())
        if leaf_transform:
            val = leaf_transform(val)

        return Tree(Node('leaf', val))

    left = create_dtree(dtree.left.left, leaf_transform)
    right = create_dtree(dtree.right.left, leaf_transform)

    identifier = dtree.node().ID().getText()
    if identifier.endswith("'"):
        if dtree.left.node().getText() == 'true':
            return left
        else:
            return right

    root = Tree(Node(identifier))
    if dtree.left.node().getText() == 'true':
        root.left = left
        root.right = right
    else:
        root.right = left
        root.left = right

    return root
