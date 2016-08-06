import sys
from os import path

from logger import logger
import model
from solver import Solver
import experiment


def main(argv):
    if len(argv) < 4:
        print('Usage: python main.py <experiment> <file> <num_futures>\n\n{}'
              .format('Supported experiments are: copycat'))
        return

    logger.info('Bulding problem instance from file')
    file_path = argv[2]
    problem_name = path.splitext(path.basename(file_path))[0]
    problem = model.from_file(file_path)

    solver = Solver(problem_name, problem, int(argv[3]), debug=False)

    experiment_name = argv[1].strip().lower()
    if experiment_name == 'copycat':
        copycat = experiment.Copycat(solver)
        copycat.start()
    else:
        print('Experiment {} is not implemented\n'.format(experiment_name))

if __name__ == '__main__':
    main(sys.argv)
