from antlr4 import *
from parser import *

from logger import logger
from builder import ModelBuilder


def from_file(model_file):
    input_stream = FileStream(model_file)

    lexer = spuddLexer(input_stream)
    token_stream = CommonTokenStream(lexer)

    logger.info("Parsing file...")
    parser = spuddParser(token_stream)
    tree = parser.init()
    logger.info("Parsing completed")

    logger.info("Building data structures...")
    model_builder = ModelBuilder()

    return model_builder.visit(tree)
