from antlr4 import *
from parser import *
from itertools import chain

from logger import logger
from copy import deepcopy

from tree.tree import Node, Tree


class SpuddVisitorImpl(spuddVisitor):

    def visitInit(self, ctx):
        problem_inst = {}

        for config in ctx.config():
            problem_inst.update(self.visit(config))

        variables = self.visit(ctx.variablesBlock())
        variables.update(self.visit(ctx.initBlock()))
        problem_inst['variables'] = variables

        actions = chain.from_iterable([self.get_actions(a)
                                       for a in ctx.actionBlock()])
        actions = list(set(actions))
        actions.reverse()
        problem_inst['actions'] = actions

        transition_tress = self.create_transition_trees(variables, actions, ctx)
        problem_inst['transition_trees'] = transition_tress

        return problem_inst

    def create_transition_trees(self, vars, actions, ctx):
        base_tree = self.create_base_trees(actions)
        return dict((v, deepcopy(base_tree)) for v in vars)

    def create_base_trees(self, actions):
        if len(actions) == 0:
            return None

        subtree_actions = actions[1:]
        left_subtree = self.create_base_trees(subtree_actions)
        right_subtree = deepcopy(left_subtree)

        return Tree(Node(actions[0]), left_subtree, right_subtree)

    def get_actions(self, ctx):
        actions_str = ctx.ID().getText()

        if actions_str == 'noop':
            return ()

        return actions_str.split('___')

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
