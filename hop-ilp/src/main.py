import sys
from os import path

import model
from solver import Solver
from mrf import MRFSolver
import experiment


def main(argv):
    if len(argv) < 4:
        print('Usage: python main.py <experiment> <file> <num_futures> [time_limit]\n\n{}'
              .format('Supported experiments are: copycat'))
        return

    file_path = argv[2]
    problem_name = path.splitext(path.basename(file_path))[0]
    problem = model.from_json_file(file_path)
    time_limit = float(argv[4]) if len(argv) > 4 else None

    if argv[1] == 'ilp':
        solver = Solver(problem_name, problem, int(argv[3]), time_limit=time_limit, debug=False)
    elif argv[1] == 'mrf':
        solver = MRFSolver(problem_name, problem, int(argv[3]), time_limit=time_limit, debug=False)
    else:
        print('Use "ilp" or "mrf" as experiment')
        return

    rddl_experiment = experiment.RDDLExperiment(solver)
    rddl_experiment.start()

if __name__ == '__main__':
    main(sys.argv)
