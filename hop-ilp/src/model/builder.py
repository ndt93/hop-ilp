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

        actions = self.get_all_actions(ctx)
        model.actions = actions

        transition_trees = TransitionTreesBuilder.\
            create_transition_trees(variables, actions, ctx.actionBlock())
        model.transition_trees = transition_trees

        reward_tree = RewardTreeBuilder.create_reward_tree(actions, ctx.actionBlock())
        model.reward_tree = reward_tree

        return model

    def get_all_actions(self, ctx):
        actions = chain.from_iterable([utils.get_actions(a)
                                       for a in ctx.actionBlock()])
        actions = list(set(actions))
        actions.reverse()
        return actions

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

        base_tree = utils.create_base_trees(actions)
        trees = dict((v, deepcopy(base_tree)) for v in variables)

        for action_block in action_blocks:
            cls.extend_trees_from_action_block(trees, action_block)

        return trees

    @classmethod
    def extend_trees_from_action_block(cls, trees, action_block):
        """
        Extends all transitions trees with trees found in an actionBlock AST
        """

        actions_str = action_block.ID().getText()
        actions = [] if actions_str == 'noop' else actions_str.split('___')

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

        dtree = cls.create_dtree(dtree)
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

    @classmethod
    def create_dtree(cls, dtree):
        """
        Creates a state transition tree from a dtree AST
        """

        if dtree.left is None and dtree.right is None:
            val = dtree.node().number().getText()
            return Tree(Node('leaf', float(val)))

        left = cls.create_dtree(dtree.left.left)
        right = cls.create_dtree(dtree.right.left)

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


class RewardTreeBuilder(object):

    @classmethod
    def create_reward_tree(cls, actions, action_blocks):
        """
        Returns a reward Tree from actionBlock+ AST

        :param actions: list of all action names
        :param action_blocks: list of actionBlock AST
        """

        base_tree = utils.create_base_trees(actions)

        for action_block in action_blocks:
            cost_block = action_block.costBlock()
            states, state_rewards = cls.get_state_rewards(cost_block)

            extended_tree = utils.create_base_trees(states)
            RewardTreeBuilder.insert_reward_leaves(extended_tree, state_rewards)

            parent = base_tree
            actions = utils.get_actions(action_block)
            while parent.left is not None and parent.right is not None:
                if parent.node.name in actions:
                    parent = parent.left
                else:
                    parent = parent.right

            if parent.node.name in actions:
                parent.left = extended_tree
            else:
                parent.right = extended_tree

        return base_tree

    @classmethod
    def insert_reward_leaves(cls, states_tree, state_rewards, accum=0):
        """
        Inserts reward values accumulated along each path of a state tree as its
        leaves. The state tree is consists of state variables as internal nodes.

        :param states_tree:
        :param state_rewards: dict of states to their corresponding rewards
        :param accum: reward accumulated from the parents of the given state tree
        """

        state = states_tree.node.name
        pos_reward = accum + state_rewards[state][0]
        neg_reward = accum + state_rewards[state][1]

        if states_tree.left is None and states_tree.right is None:
            states_tree.left = Tree(Node('leaf', pos_reward))
            states_tree.right = Tree(Node('leaf', neg_reward))
            return

        cls.insert_reward_leaves(states_tree.left, state_rewards, pos_reward)
        cls.insert_reward_leaves(states_tree.right, state_rewards, neg_reward)

    @classmethod
    def get_state_rewards(cls, cost_block):
        """
        Returns the states and their associated rewards from a cost block AST
        """
        states = []
        rewards = {}  # state => (+reward, -reward)

        for dtree in cost_block.dtree():
            state = dtree.node().ID().getText()
            pos_reward = -1 * float(dtree.left.left.node().getText())
            neg_reward = -1 * float(dtree.right.left.node().getText())

            states.append(state)
            rewards[state] = (pos_reward, neg_reward)

        return states, rewards
