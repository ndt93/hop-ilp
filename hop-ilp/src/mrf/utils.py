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
