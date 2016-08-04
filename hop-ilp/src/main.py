import sys
from os import path

from logger import logger
import model
from solver import Solver


def main(argv):
    if len(argv) < 3:
        print('Usage: python main.py <file> <num_futures>\n')
        return

    logger.info('Bulding problem instance from file')
    file_path = argv[1]
    problem_name = path.splitext(path.basename(file_path))[0]
    problem = model.from_file(file_path)

    solver = Solver(problem_name, problem, int(argv[2]), debug=False)
    actions, reward = solver.solve()

    logger.info('HOP Reward: {}'.format(reward))
    logger.info('Actions:\n{}'.format(actions))


if __name__ == '__main__':
    main(sys.argv)
