# Generated from /Users/ndt/Development/fyp/hop-ilp/res/spudd.g4 by ANTLR 4.5.3
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by spuddParser.

class spuddVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by spuddParser#init.
    def visitInit(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by spuddParser#initBlock.
    def visitInitBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by spuddParser#variablesBlock.
    def visitVariablesBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by spuddParser#variable.
    def visitVariable(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by spuddParser#actionBlock.
    def visitActionBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by spuddParser#costBlock.
    def visitCostBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by spuddParser#config.
    def visitConfig(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by spuddParser#rewardBlock.
    def visitRewardBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by spuddParser#discount.
    def visitDiscount(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by spuddParser#horizon.
    def visitHorizon(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by spuddParser#ttree.
    def visitTtree(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by spuddParser#dtree.
    def visitDtree(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by spuddParser#node.
    def visitNode(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by spuddParser#number.
    def visitNumber(self, ctx):
        return self.visitChildren(ctx)


