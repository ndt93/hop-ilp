import sys
from os import path

import model
from solver.spec.ilp_sysadmin import ILPSysadmin
from solver.spec.ilp_gol import ILPGol
from solver.spec.ilp_nav import ILPNav
from solver.spec.ilp_elevators import ILPElevators
from solver.spec.ilp_copycat import ILPCopycat

from mrf.spec.mrf_sysadmin import SysAdminMRF
from mrf.spec.mrf_gol import GolMRF
from mrf.spec.mrf_nav2 import NavMRF
from mrf.spec.mrf_elevators import ElevatorsMRF
from mrf.spec.mrf_copycat import CopycatMRF

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

    base_args = (problem_name, problem, int(argv[3]))
    base_kwards = {'time_limit': time_limit, 'debug': False}

    if argv[1] == 'ilp':
        if problem_name.startswith('sysadmin'):
            solver = ILPSysadmin(*base_args, **base_kwards)
        elif problem_name.startswith('game_of_life'):
            solver = ILPGol(*base_args, **base_kwards)
        elif problem_name.startswith('navigation'):
            solver = ILPNav(*base_args, **base_kwards)
        elif problem_name.startswith('elevators'):
            solver = ILPElevators(*base_args, **base_kwards)
        elif problem_name.endswith('copycat'):
            solver = ILPCopycat(*base_args, **base_kwards)
    elif argv[1] == 'mrf':
        if problem_name.startswith('sysadmin'):
            solver = SysAdminMRF(*base_args, **base_kwards)
        elif problem_name.startswith('game_of_life'):
            solver = GolMRF(*base_args, **base_kwards)
        elif problem_name.startswith('navigation'):
            solver = NavMRF(*base_args, **base_kwards)
        elif problem_name.startswith('elevators'):
            solver = ElevatorsMRF(*base_args, **base_kwards)
        elif problem_name.endswith('copycat'):
            solver = CopycatMRF(*base_args, **base_kwards)
    else:
        print('Use "ilp" or "mrf" as experiment')
        return

    rddl_experiment = experiment.RDDLExperiment(solver)
    rddl_experiment.start()

if __name__ == '__main__':
    main(sys.argv)
