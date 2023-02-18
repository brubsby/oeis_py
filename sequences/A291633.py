import itertools
import sys
import random

import marisa_trie
from bitarray import bitarray
import logging

from sequence import Sequence

__highest_n = 100000
__lookup = ["{0:b}".format(i) for i in range(__highest_n + 1)]


def can_mid(midlen, midstr, midpos):
    if midpos % 2 == 0:  # even
        normal_index = midpos // 2
        i = 0
        while i < midlen - normal_index and i < normal_index:
            if midstr[i + normal_index] != midstr[normal_index - i - 1]:
                return False
            i += 1
        return True
    else:  # odd
        normal_index = (midpos - 1) // 2
        i = 0
        while i < midlen - normal_index - 1 and i < normal_index:
            if midstr[i + normal_index + 1] != midstr[normal_index - i - 1]:
                return False
            i += 1
        return True


def split_mid(midstr, midpos):
    if midpos % 2 == 0:  # even
        normal_index = midpos // 2
        return midstr[normal_index:], midstr[:normal_index], ""
    else:  # odd
        normal_index = (midpos - 1) // 2
        return midstr[normal_index+1:], midstr[:normal_index], midstr[normal_index]


def get_zeroest_number(numbers, lookup):
    most_zeros = 0
    most_zeros_number = None
    for number in numbers:
        num_zeros = lookup[number].count("0")
        if num_zeros > most_zeros:
            most_zeros = num_zeros
            most_zeros_number = number
    return most_zeros_number


def get_big_zeros_midpos(number, lookup):
    binary_str = lookup[number]
    num_zeros = binary_str.count("0")
    passed_zeros = 0
    index = 1
    if num_zeros % 2 == 0:
        while passed_zeros < num_zeros // 2:
            if binary_str[index] == "0":
                passed_zeros += 1
            index += 1
        return index * 2
    else:
        while passed_zeros < num_zeros // 2:
            if binary_str[index] == "0":
                passed_zeros += 1
            index += 1
        return index * 2 + 1


def count_zero_groups(numbers, lookup):
    zero_groups_count = {}
    for number in numbers:
        for group in lookup[number].split("1"):
            count = len(group)
            if count > 0:
                zero_groups_count[count] = 1 + (zero_groups_count.get(count) or 0)
    return zero_groups_count


def count_zero_groups_concat_str(concat_str):
    zero_groups_count = {}
    for group in concat_str.split("1"):
        count = len(group)
        if count > 0:
            zero_groups_count[count] = 1 + (zero_groups_count.get(count) or 0)
    return zero_groups_count


def test_depth_first_stochastic(n):
    if n == 1:
        return "|1|"
    lookup = ["{0:b}".format(i) for i in range(n+1)]
    lenlookup = [len("{0:b}".format(i)) for i in range(n+1)]
    revlookup = [lookup[i][::-1] for i in range(n+1)]
    numbers = [i for i in range(1, n+1)]
    tumbers = [(i,) for i in range(1, n+1)]
    strings = [lookup[i] for i in numbers]
    revstrings = [revlookup[i] for i in numbers]
    fmt = "<H"
    trie = marisa_trie.RecordTrie(fmt, zip(strings, tumbers))
    revtrie = marisa_trie.RecordTrie(fmt, zip(revstrings, tumbers))
    used = bitarray(n+1)
    used.setall(0)
    midnum = get_zeroest_number(numbers, lookup)
    midnum_midpos = get_big_zeros_midpos(midnum, lookup)
    while True:
        forward, backward, midchar = split_mid(lookup[midnum], midnum_midpos)
        retstr = f"{backward}{'|{}|'.format(midchar) if len(midchar) else '|'}{forward}"
        used.setall(0)
        used[midnum] = True
        stack = []
        popped_options = []
        while True:
            forward_len = len(forward)
            backward_len = len(backward)

            if not popped_options:
                if forward_len < backward_len:
                    build_front = True
                    prefix = backward[-forward_len-1:-1-backward_len:-1]
                elif backward_len < forward_len:
                    build_front = False
                    prefix = forward[backward_len:forward_len]
                else:
                    prefix = ""
                    build_front = True

                if build_front:
                    to_try = trie.items(prefix)
                else:
                    to_try = revtrie.items(prefix)

                can_try = [record for record in to_try if not used[record[1][0]]]
                if len(can_try) > 1:
                    random.shuffle(can_try)
            else:
                build_front = forward_len <= backward_len
                can_try = popped_options
            if len(can_try) > 0:
                record = can_try.pop()
            else:
                retstr, forward, backward, used, popped_options = stack.pop()
                continue
            if len(can_try) > 0:
                stack.append((retstr, forward, backward, used.copy(), can_try))
            used[record[1][0]] = True
            if used.count(1) >= n:
                if build_front:
                    if forward_len + lenlookup[record[1][0]] == backward_len:
                        return retstr + f".{record[0]}"
                    else:
                        retstr, forward, backward, used, popped_options = stack.pop()
                else:
                    if forward_len == backward_len + lenlookup[record[1][0]]:
                        return f"{lookup[record[1][0]]}." + retstr
                    else:
                        retstr, forward, backward, used, popped_options = stack.pop()
            else:
                if build_front:
                    forward = forward + record[0]
                    retstr = retstr + f".{record[0]}"
                else:
                    backward = lookup[record[1][0]] + backward
                    retstr = f"{lookup[record[1][0]]}." + retstr
                popped_options = []


def sort_val(string, base=10):
    groupings = count_zero_groups_concat_str(string)
    score = 0
    for grouping, count in groupings.items():
        score += int(pow(base, grouping)) * count
    return score


def test_depth_first_stochastic2(n, count_limit=None):
    if n == 1:
        return "|1|"
    lookup = ["{0:b}".format(i) for i in range(n+1)]
    lenlookup = [len("{0:b}".format(i)) for i in range(n+1)]
    revlookup = [lookup[i][::-1] for i in range(n+1)]
    numbers = [i for i in range(1, n+1)]
    strings = [lookup[i] for i in numbers]
    revstrings = [revlookup[i] for i in numbers]
    stringlookup = dict([(lookup[i], i) for i in range(n+1)])
    revstringlookup = dict([(revlookup[i], i) for i in range(n+1)])
    sortlookup = [sort_val(lookup[i], n) for i in range(n+1)]
    trie = marisa_trie.Trie(strings)
    revtrie = marisa_trie.Trie(revstrings)
    used = bitarray(n+1)
    used.setall(0)
    midnum = get_zeroest_number(numbers, lookup)
    midnum_midpos = get_big_zeros_midpos(midnum, lookup)
    while True:
        forward, backward, midchar = split_mid(lookup[midnum], midnum_midpos)
        retstr = f"{backward}{'|{}|'.format(midchar) if len(midchar) else '|'}{forward}"
        used.setall(0)
        used[midnum] = True
        stack = []
        popped_options = []
        count = 0
        while True:
            count += 1
            if count_limit and count > count_limit:
                break
            forward_len = len(forward)
            backward_len = len(backward)

            if not popped_options:
                if forward_len < backward_len:
                    build_front = True
                    prefix = backward[-forward_len-1:-1-backward_len:-1]
                elif backward_len < forward_len:
                    build_front = False
                    prefix = forward[backward_len:forward_len]
                else:
                    prefix = ""
                    build_front = True

                if build_front:
                    to_try = [stringlookup[string] for string in trie.keys(prefix)]
                else:
                    to_try = [revstringlookup[string] for string in revtrie.keys(prefix)]

                can_try = [number for number in to_try if not used[number]]
                if can_try:
                    random.shuffle(can_try)
                    # can_try = sorted(can_try, key=lambda x: sortlookup[x])
            else:
                build_front = forward_len <= backward_len
                can_try = popped_options
            if len(can_try) > 0:
                record = can_try.pop()
            else:
                retstr, forward, backward, used, popped_options = stack.pop()
                continue
            if len(can_try) > 0:
                stack.append((retstr, forward, backward, used.copy(), can_try))
            used[record] = True
            if used.count(1) >= n:
                if build_front:
                    if forward_len + lenlookup[record] == backward_len:
                        print(count)
                        return retstr + f".{lookup[record]}"
                    else:
                        retstr, forward, backward, used, popped_options = stack.pop()
                else:
                    if forward_len == backward_len + lenlookup[record]:
                        print(count)
                        return f"{lookup[record]}." + retstr
                    else:
                        retstr, forward, backward, used, popped_options = stack.pop()
            else:
                if build_front:
                    forward = forward + lookup[record]
                    retstr = retstr + f".{lookup[record]}"
                else:
                    backward = lookup[record] + backward
                    retstr = f"{lookup[record]}." + retstr
                popped_options = []


def failfast(n, concat_str=None):  # lookup table of n such that the binary digit counts are both odd
    if n == 1:
        return True
    if not concat_str:
        concat_str = "".join(__lookup[1:n+1])
    num_ones = concat_str.count("1")
    if num_ones % 2 == 1:
        return False
    zero_group_counts = count_zero_groups_concat_str(concat_str)
    first = True
    for i in reversed(zero_group_counts.keys()):
        if first:
            if zero_group_counts[i] % 2 != 1:
                return False  # biggest zero group must be odd in count
            first = False
        else:
            if zero_group_counts[i] % 2 != 0:
                return False
    return True


class A291633(Sequence):

    def __init__(self):
        super().__init__(start_index=1,
                         lookup_list=[1, 2, 3, 11, 20, 22, 42, 43, 82, 162, 171, 322, 340, 342, 642, 682, 683, 1282,
                                      1362, 2562, 2722, 2731,
                                      5122, 5442, 5460, 5462, 10242, 10882, 10922, 10923, 20482, 21762, 21842, 40962,
                                      43522, 43682, 43691, 81922,
                                      87042, 87362, 87380, 87382, 163842, 174082, 174722, 174762, 174763])

    def calculate(self, n):
        if n == 1:
            return 1
        k = self.load_checkpoint(self(n-1)+1, n=n)
        concat_str = "".join(["{0:b}".format(i) for i in range(1, k + 1)])
        for k in itertools.count(start=k):
            if failfast(k, concat_str=concat_str):
                self.delete_checkpoint(n=n)
                return k
            concat_str += f"{k+1:b}"
            self.checkpoint(k, k, 10000, n=n)

    def find_example(self, n, count_limit=None):
        if failfast(n):
            permutation = test_depth_first_stochastic2(n, count_limit=count_limit)
            if permutation:
                return permutation

    # overriding generate for algorithmic performance reasons
    def generator(self, start):
        one_count = 0
        zero_groups = {}
        yield 1
        for k in itertools.count(start=start):
            this_str = "{0:b}".format(k)
            one_count += this_str.count("1")
            this_zero_groups = count_zero_groups_concat_str(this_str)
            for key, value in this_zero_groups.items():
                zero_groups[key] = zero_groups.get(key, 0) + value
            if one_count % 2 == 0:
                groups = sorted(zero_groups.keys())
                if zero_groups[groups[-1]] % 2 == 1:
                    fail = False
                    for group in groups[:-1]:
                        if zero_groups[group] % 2 == 1:
                            fail = True
                            break
                    if not fail:
                        yield k


sys.modules[__name__] = A291633()


def newseq(n, concat_str=None):  # lookup table of n such that the binary digit counts are both odd
    if n == 1:
        return True
    if not concat_str:
        concat_str = "".join(__lookup[1:n + 1])
    zero_group_counts = count_zero_groups_concat_str(concat_str)
    first = True
    for i in reversed(zero_group_counts.keys()):
        if first:
            if zero_group_counts[i] % 2 != 1:
                return False  # biggest zero group must be odd in count
            first = False
        else:
            if zero_group_counts[i] % 2 != 0:
                return False
    return True


def newseq2():
    one_count = 0
    zero_groups = {}
    for k in itertools.count(start=1):
        this_str = "{0:b}".format(k)
        one_count += this_str.count("1")
        this_zero_groups = count_zero_groups_concat_str(this_str)
        for key, value in this_zero_groups.items():
            zero_groups[key] = zero_groups.get(key, 0) + value
        groups = sorted(zero_groups.keys())
        if not groups:
            yield k
            continue
        if zero_groups[groups[-1]] % 2 == 1:
            fail = False
            for group in groups[:-1]:
                if zero_groups[group] % 2 == 1:
                    fail = True
                    break
            if not fail:
                yield k


if __name__ == "__main__":
    for i in newseq2():
        print(i, end=", ")
    # A291633().generate_b_file(max_n=100)
    # start_val = 1
    # for n, val in A291633().enumerate():
    #     if val != -1:
    #         print(f"{n+start_val} {val}")


