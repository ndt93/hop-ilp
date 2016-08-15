from base import Experiment
from client import Client
from logger import logger


class RDDLExperiment(Experiment):
    client = None
    session_info = {}

    def start(self):
        self.solver.solve()
        self.client = Client('python-client')
        self.session_info = self.client.request_session(self.solver.problem_name)
        logger.info('session_start|session={}'.format(self.session_info));

        session_end_info = self.loop_rounds()
        logger.info('session_end|info={}'.format(session_end_info))

    def loop_rounds(self):
        while True:
            round_info = self.client.request_round()
            logger.info('round_start|round={}'.format(round_info));

            t, end_info = self.loop_turns()
            if t != 'round':
                return end_info
            logger.info('round_end|info={}'.format(end_info))

    def loop_turns(self):
        while True:
            t, data = self.client.receive_turn()
            if t != 'turn':
                return t, data

            states = self.get_states_from_turn(data)

    def get_states_from_turn(self, turn):
        pass
