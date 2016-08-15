from base import Experiment
from client import Client


class RDDLExperiment(Experiment):
    client = None
    session_info = {}

    def start(self):
        self.client = Client('python-client')
        self.session_info = self.client.request_session(self.solver.problem_name)
