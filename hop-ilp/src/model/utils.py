from tree import Node, Tree


def create_base_trees(variables, paths):
    """
    Creates a Tree by combining paths
    """

    result = None

    for p in paths:
        prev_tree = None
        prev_val = None
        cur_tree = result

        for v in variables:
            if cur_tree is None:
                cur_tree = Tree(Node(v))
                if prev_tree is None:
                    result = cur_tree
                else:
                    if prev_val:
                        prev_tree.left = cur_tree
                    else:
                        prev_tree.right = cur_tree
                prev_tree = cur_tree
                prev_val = v in p
                cur_tree = None
            else:
                prev_tree = cur_tree
                prev_val = v in p
                if prev_val:
                    cur_tree = cur_tree.left
                else:
                    cur_tree = cur_tree.right

    return result


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
    if left is None and right is None:
        return None

    identifier = dtree.node().ID().getText()
    if identifier.endswith("'"):
        if dtree.left.node().getText() == 'true':
            return left if left.node.value >= 1e-6 else None
        else:
            return right if right.node.value >= 1e-6 else None

    root = Tree(Node(identifier))
    if dtree.left.node().getText() == 'true':
        root.left = left
        root.right = right
    else:
        root.right = left
        root.left = right

    return root


def get_all_actions_groups(action_blocks):
    return [get_actions_group(action_block) for action_block in action_blocks]


def get_actions_group(action_block):
    actions_str = action_block.ID().getText()
    return [] if actions_str == 'noop' else actions_str.split('___')
