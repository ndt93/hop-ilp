import sys

if sys.version_info[0] < 3:
    input = raw_input


class Experiment(object):

    def __init__(self, solver):
        self.solver = solver

    def start(self):
        pass

    @staticmethod
    def str_sorted_dict(d):
        l = []
        for key in sorted(d):
            l.append('{} = {}'.format(key, d[key]))

        return ', '.join(l)
