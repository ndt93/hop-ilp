from antlr4 import *
from parser import *


class SpuddVisitorImpl(spuddVisitor):

	def visitInit(self, ctx):
		all_config = {}
		for config in ctx.config():
			all_config.update(self.visit(config))

		return all_config

	def visitHorizon(self, ctx):
		return {"horizon": int(ctx.val.INT().getText())}

	def visitDiscount(self, ctx):
		return {}

	def visitRewardBlock(self, ctx):
		return {}


class ProblemBuilder(object):

	def from_file(self, model_file):
		input_stream = FileStream(model_file)

		lexer = spuddLexer(input_stream)
		token_stream = CommonTokenStream(lexer)

		parser = spuddParser(token_stream)
		tree = parser.init()

		evaluator = SpuddVisitorImpl()
		print evaluator.visit(tree)
