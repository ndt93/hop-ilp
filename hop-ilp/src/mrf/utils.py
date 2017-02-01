import mrf
import mrf.mrf_clique

def count_set_bits(n):
    count = 0
    while n != 0:
        count += 1
        n &= n - 1
    return count


def stringify(l):
    return [str(x) for x in l]


def write_line(f, l):
    f.write('{}\n'.format(l))


def print_MAP(map_assignments, problem, num_futures):
    mdp_states = list(problem.variables)
    mdp_actions = list(problem.actions)
    mdp_states.sort()
    mdp_actions.sort()

    for k in range(num_futures):
        print('Future %d' % k)
        for t in range(problem.horizon):
            print(' Horizon: %d' % t)
            for s in mdp_states:
                print('  %s: %d' % (s, map_assignments[(s, k, t)]))
            for a in mdp_actions:
                print('  %s: %d' % (a, map_assignments[(a, k, t)]))


def is_set(bitmask, idx):
    # type: (int, int) -> bool
    return (bitmask & (1 << idx)) != 0


def match_determinized_val(bitmask, idx, determinized_val):
    # type: (int, int, int) -> bool
    return is_set(bitmask, idx) == (determinized_val == 1)


def append_function_entry(clique, bitmask, idx, val, invalid_val=mrf.INVALID_POTENTIAL_VAL):
    # type: (mrf.mrf_clique.MRFClique, int, int, int, float) -> None
    if match_determinized_val(bitmask, idx, val):
        clique.function_table.append(1)
    else:
        clique.function_table.append(invalid_val)


def count_set_bit(bitmask, start, end):
    """
    Counts number of set bit in bitmask[start:end]
    """
    count = 0
    i = 1 << start
    for _ in range(end - start):
        if bitmask & i != 0:
            count += 1
        i <<= 1
    return count


