import sys

from logger import logger
import model


def main(argv):
    if len(argv) < 2:
        print("Usage: python main.py <file>\n")
        return

    logger.info("Bulding problem instance from file")
    problem = model.from_file(argv[1])
    problem.log_transition_trees()
    problem.log_reward_tree()


if __name__ == "__main__":
    main(sys.argv)
