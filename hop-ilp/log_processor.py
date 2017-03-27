import sys
import re


def get_round_stats(l):
    ret = {'round_reward': None, 'turns_used': None, 'time_used': None}

    matches = re.search(r"\(u'round-reward', u'(-?\d+(\.\d+)?)'\)", l)
    if matches:
        ret['round_reward'] = float(matches.group(1))

    matches = re.search(r"\(u'turns-used', u'(\d+)'\)", l)
    if matches:
        ret['turns_used'] = int(matches.group(1))

    matches = re.search(r"\(u'time-used', u'(\d+)'\)", l)
    if matches:
        ret['time_used'] = int(matches.group(1))

    return ret


def get_session_stats(l):
    ret = {'total_reward': None, 'rounds_used': None, 'time_used': None}

    matches = re.search(r"\(u'total-reward', u'(-?\d+(\.\d+)?)'\)", l)
    if matches:
        ret['total_reward'] = float(matches.group(1))

    matches = re.search(r"\(u'rounds-used', u'(\d+)'\)", l)
    if matches:
        ret['rounds_used'] = int(matches.group(1))

    matches = re.search(r"\(u'time-used', u'(\d+)'\)", l)
    if matches:
        ret['time_used'] = int(matches.group(1))

    return ret


def main():
    num_turns = 0
    num_rounds = 0
    total_reward = 0

    with open(sys.argv[1], 'r') as f:
        for l in f:
            if l.find('round_end') != -1:
                num_rounds += 1
                round_stats = get_round_stats(l)
                if round_stats['turns_used']:
                    num_turns += round_stats['turns_used']
                print('round reward: %6.3lf, turns used: %3d, time used: %5d'
                      % (round_stats['round_reward'],
                         round_stats['turns_used'],
                         round_stats['time_used']))
            elif l.find('session_end') != -1:
                session_stats = get_session_stats(l)
                total_reward = session_stats['total_reward']
                print('--------------------')
                print('Total Reward: %.3lf\nAverage Reward: %.3f' %
                      (total_reward, total_reward/num_turns))
                print('Rounds used: %d/%d\nTime used: %d' %
                      (num_rounds, session_stats['rounds_used'],
                       session_stats['time_used']))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python log_processor.py <log_file>')
        sys.exit(1)
    main()
