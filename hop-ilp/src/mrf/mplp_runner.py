from logger import logger
from subprocess import Popen
import os
import mrf


class MPLPRunner(object):

    def __init__(self, actions, idx_to_var, time_limit=None):
        self.actions = actions
        self.idx_to_var = idx_to_var
        self.time_limit = time_limit

    def run_mplp(self):
        logger.info('executing_mplp_solver|exec=%s' % mrf.MPLP_EXEC)
        mplp_env = os.environ.copy()
        if self.time_limit is not None:
            mplp_env['INF_TIME'] = str(self.time_limit)

        fdevnull = open(os.devnull, 'w')
        #fdevnull = None
        mplp_proc = Popen([mrf.MPLP_EXEC, mrf.OUTPUT_FILE], env=mplp_env, stdout=fdevnull)
        mplp_proc.wait()
        if fdevnull is not None:
            fdevnull.close()
        logger.info('execution_completed|returncode=%s' % mplp_proc.returncode)
        return self.get_MAP_assignments()

    def get_next_actions(self, map_assignments):
        result = {}
        for action in self.actions:
            result[action] = map_assignments[(action, 0, 0)]
        return result

    def get_MAP_assignments(self):
        map_assignments = {}

        with open(mrf.RESULT_FILE, 'r') as outfile:
            for l in outfile:
                pass
            l = l.rstrip().split(' ')

            assert(len(l) == len(self.idx_to_var) + 1)
            for i, v in enumerate(l[1:]):
                map_assignments[self.idx_to_var[i]] = int(v)

        return map_assignments
