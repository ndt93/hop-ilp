import sys
from os import path

import model
from solver import Solver
from mrf.spec.mrf_sysadmin import SysAdminMRF
from mrf.spec.mrf_gol import GolMRF
from mrf.spec.mrf_nav import NavMRF
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
        base_args = (problem_name, problem, int(argv[3]))
        base_kwards = {'time_limit': time_limit, 'debug': True}

        if problem_name.startswith('sysadmin'):
            solver = SysAdminMRF(*base_args, **base_kwards)
        elif problem_name.startswith('game_of_life'):
            solver = GolMRF(*base_args, **base_kwards)
        elif problem_name.startswith('navigation'):
            solver = NavMRF(*base_args, **base_kwards)
            solver.solve()
    else:
        print('Use "ilp" or "mrf" as experiment')
        return

    # rddl_experiment = experiment.RDDLExperiment(solver)
    # rddl_experiment.start()

if __name__ == '__main__':
    main(sys.argv)
