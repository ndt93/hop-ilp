import sys

if sys.version_info[0] < 3:
    input = raw_input


class Experiment(object):

    def __init__(self, solver):
        self.solver = solver

    def start(self):
        pass
