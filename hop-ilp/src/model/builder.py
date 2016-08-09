from parser import *
from copy import deepcopy
from itertools import chain

from tree import Node, Tree
from model import Model
import utils


class ModelBuilder(spuddVisitor):

    def visitInit(self, ctx):
        model = Model()

        for config in ctx.config():
            model.__dict__.update(self.visit(config))

        variables = self.get_variables(ctx)
        model.variables = variables

        actions, max_concurrency = self.get_all_actions(ctx)
        model.actions = actions
        model.max_concurrency = max_concurrency

        transition_trees = TransitionTreesBuilder.\
            create_transition_trees(variables, actions, ctx.actionBlock())
        model.transition_trees = transition_trees

        reward_tree = RewardTreeBuilder.create_reward_tree(actions, ctx.actionBlock())
        model.reward_tree = reward_tree

        return model

    def get_all_actions(self, ctx):
        actions_groups = utils.get_all_actions_groups(ctx.actionBlock())

        actions = chain.from_iterable(actions_groups)
        actions = list(set(actions))
        actions.reverse()

        max_concurrency = max([len(g) for g in actions_groups])

        return actions, max_concurrency

    def get_variables(self, ctx):
        variables = self.visit(ctx.variablesBlock())
        variables.update(self.visit(ctx.initBlock()))
        return variables

    def visitVariablesBlock(self, ctx):
        variables = [self.visit(v) for v in ctx.variable()]
        return {v: 0 for v in variables}

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


class TransitionTreesBuilder(object):
    @classmethod
    def create_transition_trees(cls, variables, actions, action_blocks):
        """
        Returns a dictionary of state variables to their transition trees. Each tree
        consists of a base tree created from all combinations of actions values

        :param variables: list of all state variables literals
        :param actions: list of all actions literals
        :param action_blocks: list of all actionBlock AST
        """

        actions_groups = utils.get_all_actions_groups(action_blocks)
        base_tree = utils.create_base_trees(actions, actions_groups)
        trees = {v: deepcopy(base_tree) for v in variables}

        for action_block in action_blocks:
            cls.extend_trees_from_action_block(trees, action_block)

        return trees

    @classmethod
    def extend_trees_from_action_block(cls, trees, action_block):
        """
        Extends all transitions trees with trees found in an actionBlock AST
        """
        actions = utils.get_actions_group(action_block)

        for ttree in action_block.ttree():
            cls.extend_base_tree(trees[ttree.ID().getText()],
                                 ttree.dtree(),
                                 actions)

    @classmethod
    def extend_base_tree(cls, base_tree, dtree, actions):
        """
        Extends a base tree of a state by inserting a transition tree to
        an appropriate path following the list of positive action literals.

        The base tree will be modified in place
        """

        dtree = utils.create_dtree(dtree)
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


class RewardTreeBuilder(object):

    @classmethod
    def create_reward_tree(cls, actions, action_blocks):
        """
        Returns a reward Tree from actionBlock+ AST. The returned reward tree
        is an extended Tree whose leaves' values contain a list of multiple subtrees

        :param actions: list of all action names
        :param action_blocks: list of actionBlock AST
        """

        actions_groups = utils.get_all_actions_groups(action_blocks)
        base_tree = utils.create_base_trees(actions, actions_groups)

        for action_block in action_blocks:
            cost_block = action_block.costBlock()
            reward_trees = []

            for dtree in cost_block.dtree():
                reward_trees.append(utils.create_dtree(dtree, lambda l: -l))

            parent = base_tree
            actions = utils.get_actions_group(action_block)
            while parent.left is not None and parent.right is not None:
                if parent.node.name in actions:
                    parent = parent.left
                else:
                    parent = parent.right

            extended_tree = Tree(Node('branches', reward_trees))
            if parent.node.name in actions:
                parent.left = extended_tree
            else:
                parent.right = extended_tree

        return base_tree
