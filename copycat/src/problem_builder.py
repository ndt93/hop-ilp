from antlr4 import *
from parser import *
from itertools import chain

from logger import logger
from copy import deepcopy

from tree.tree import Node, Tree


class SpuddVisitorImpl(spuddVisitor):

    def visitInit(self, ctx):
        """
        Constructs a problem instance from the AST
        """

        problem_inst = {}

        for config in ctx.config():
            problem_inst.update(self.visit(config))

        variables = self.get_variables(ctx)
        problem_inst['variables'] = variables

        actions = self.get_all_actions(ctx)
        problem_inst['actions'] = actions

        transition_trees = self.create_transition_trees(variables, actions, ctx)
        problem_inst['transition_trees'] = transition_trees

        return problem_inst

    def create_transition_trees(self, variables, actions, ctx):
        """
        Returns a dictionary of state variables to their transition trees. Each tree
        consists of a base tree created from all combinations of actions values

        :param variables: list of all state variables literals
        :param actions: list of all actions literals
        :param ctx: list of all actionBlock
        """

        base_tree = self.create_base_trees(actions)
        trees = dict((v, deepcopy(base_tree)) for v in variables)

        for action_block in ctx.actionBlock():
            self.extend_trees_from_action_block(trees, action_block)

        return trees

    def extend_trees_from_action_block(self, trees, action_block):
        """
        Extends all transitions trees with trees found in an actionBlock AST
        """

        actions_str = action_block.ID().getText()
        actions = [] if actions_str == 'noop' else actions_str.split('___')

        for ttree in action_block.ttree():
            self.extend_base_tree(trees[ttree.ID().getText()],
                                  ttree.dtree(),
                                  actions)

    def extend_base_tree(self, base_tree, dtree, actions):
        """
        Extends a base tree of a state by inserting a transition tree to
        an appropriate path following the list of positive action literals.

        The base tree will be modified in place
        """

        dtree = self.create_dtree(dtree)
        parent = base_tree

        while parent.left is not None and parent.right is not None:
            if parent.node.name in actions:
                parent = parent.left
            else:
                parent = parent.right

        if parent.node.name in actions:
            parent.left = dtree
        else:
            parent.right = dtree

    def create_dtree(self, dtree):
        """
        Creates a state transition tree from a dtree AST
        """

        if dtree.left is None and dtree.right is None:
            val = dtree.node().number().getText()
            return Tree(Node('leaf', float(val)))

        left = self.create_dtree(dtree.left.left)
        right = self.create_dtree(dtree.right.left)

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

    def create_base_trees(self, actions):
        if len(actions) == 0:
            return None

        subtree_actions = actions[1:]
        left_subtree = self.create_base_trees(subtree_actions)
        right_subtree = deepcopy(left_subtree)

        return Tree(Node(actions[0]), left_subtree, right_subtree)

    def get_all_actions(self, ctx):
        actions = chain.from_iterable([self.get_actions(a)
                                       for a in ctx.actionBlock()])
        actions = list(set(actions))
        actions.reverse()
        return actions

    def get_actions(self, ctx):
        actions_str = ctx.ID().getText()

        if actions_str == 'noop':
            return ()

        return actions_str.split('___')

    def get_variables(self, ctx):
        variables = self.visit(ctx.variablesBlock())
        variables.update(self.visit(ctx.initBlock()))
        return variables

    def visitVariablesBlock(self, ctx):
        variables = [self.visit(v) for v in ctx.variable()]
        return dict((v, 0) for v in variables)

    def visitVariable(self, ctx):
        return ctx.ID().getText()

    def visitInitBlock(self, ctx):
        vars_init = [self.visit_var_init_clause(v) for v in ctx.dtree()]
        return dict(v for v in vars_init)

    def visit_var_init_clause(self, ctx):
        var_name = ctx.node().getText()

        if ctx.left.left.node().getText() == '1.0':
            return var_name, 1

        return var_name, 0

    def visitHorizon(self, ctx):
        return {'horizon': int(ctx.val.INT().getText())}

    def visitDiscount(self, ctx):
        return {}

    def visitRewardBlock(self, ctx):
        return {}


class ProblemBuilder(object):
    problem_inst = {}

    def from_file(self, model_file):
        input_stream = FileStream(model_file)

        lexer = spuddLexer(input_stream)
        token_stream = CommonTokenStream(lexer)

        logger.info("Parsing file...")
        parser = spuddParser(token_stream)
        tree = parser.init()
        logger.info("Parsing completed")

        logger.info("Building data structures...")
        evaluator = SpuddVisitorImpl()

        self.problem_inst = evaluator.visit(tree)
        for v, t in self.problem_inst['transition_trees'].items():
            logger.info('{}\n{!s}'.format(v, t))
