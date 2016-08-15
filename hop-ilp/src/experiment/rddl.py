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

            logger.info('turn|num={},time_left={},im_reward={}'
                        .format(data['turn-num'], data['time-left'], data['immediate-reward']))
            states = RDDLExperiment.get_states_from_turn(data)
            logger.debug('states={}'.format(states))
            self.solver.init_next_step(states)
            actions, _ = self.solver.solve()
            self.client.send_actions(RDDLExperiment.format_actions(actions))

    @staticmethod
    def format_actions(actions):
        result = {}
        action_blks = [RDDLExperiment.format_action(a)
                       for a, v in actions.items() if v == 1]

        if len(action_blks) == 0:
            result['actions'] = None
        elif len(action_blks) == 1:
            result['actions'] = {'action': action_blks[0]}
        else:
            result['actions'] = {'action': action_blks}

        return result

    @staticmethod
    def format_action(a):
        action_blk = {}
        parts = a.split('__')

        action_blk['action-name'] = parts[0]

        if len(parts) == 2:
            action_blk['action-arg'] = parts[1]
        elif len(parts) > 2:
            action_blk['action-arg'] = parts[1:]

        action_blk['action-value'] = 'true'

        return action_blk

    @staticmethod
    def get_states_from_turn(turn):
        if 'no-observed-fluents' in turn:
            return {}

        result = {}
        for fluent in turn['observed-fluent']:
            state_name = RDDLExperiment.get_compound_fluent_name(fluent)
            state_val = 1 if fluent['fluent-value'] == 'true' else 0
            result[state_name] = state_val

        return result

    @staticmethod
    def get_compound_fluent_name(fluent):
        fluent_name = fluent['fluent-name'].replace('-', '_')
        if 'fluent-arg' not in fluent:
            return fluent_name
        fluent_arg = fluent['fluent-arg']

        if isinstance(fluent_arg, list):
            l = ['{}_'.format(fluent_name)]
            l.extend(fluent_arg)
            return '_'.join(l)
        else:
            return '{}__{}'.format(fluent_name, fluent_arg)
