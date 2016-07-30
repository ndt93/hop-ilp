class Node(object):

    def __init__(self, name="", value=None):
        self.name = name
        self.value = value

    def __str__(self):
        if self.value is None:
            return self.name

        return '{}#{}'.format(self.name, self.value)


class Tree(object):

    def __init__(self, node=Node(), left=None, right=None):
        self.node = node
        self.left = left
        self.right = right

    def __str__(self):
        if self.left is None and self.right is None:
            return str(self.node)

        node_str = str(self.node)
        padding = ' ' * (len(node_str) / 2)
        left_split = str(self.left).split('\n')
        right_split = str(self.right).split('\n')

        left_split[0] = '{}|-- {}'.format(padding, left_split[0])
        right_split[0] = '{}|-- {}'.format(padding, right_split[0])
        left_split[1:] = ['{}|   {}'.format(padding, l) for l in left_split[1:]]
        right_split[1:] = ['{}    {}'.format(padding, l) for l in right_split[1:]]

        left_str = '\n'.join(left_split)
        right_str = '\n'.join(right_split)

        return '{}\n{}\n{}'.format(self.node, left_str, right_str)
