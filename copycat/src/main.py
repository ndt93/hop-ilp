import sys

from problem_builder import ProblemBuilder
from logger import logger


def main(argv):
    if len(argv) < 2:
        print("Usage: python main.py <file>\n")
        return

    logger.info("Bulding problem instance from file")
    builder = ProblemBuilder()
    builder.from_file(argv[1])


if __name__ == "__main__":
    main(sys.argv)
