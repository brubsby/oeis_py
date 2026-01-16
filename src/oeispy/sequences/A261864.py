import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence
from bitarray import bitarray

import gmpy2


def is_reversible(rule, reversible_neighborhood_map):
    for neighborhood, rev_neighborhood in reversible_neighborhood_map.items():
        if rule.bit_test(neighborhood) != rule.bit_test(rev_neighborhood):
            return False
    return True


class A261864(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0)

    def calculate(self, n):
        num_neighborhoods = pow(2, n)
        num_rules = pow(2, num_neighborhoods)
        rule = gmpy2.mpz(0)
        # maps a neighborhood to its bit reversed equivalent
        # both of these neighborhoods must produce the same result for a rule to be equivalent
        reversible_neighborhood_map = {}
        neighborhood = gmpy2.xmpz(0)
        while neighborhood < num_neighborhoods:
            rev_neighborhood = gmpy2.mpz()
            for bit in neighborhood.iter_set():
                rev_neighborhood = rev_neighborhood.bit_set(n-bit-1)
            if neighborhood != rev_neighborhood and rev_neighborhood not in reversible_neighborhood_map:
                reversible_neighborhood_map[gmpy2.mpz(neighborhood)] = rev_neighborhood
            neighborhood += 1

        reversible_rule_count = 0
        while rule < num_rules:
            if is_reversible(rule, reversible_neighborhood_map):
                # print(rule)
                reversible_rule_count += 1
            rule += 1
        return reversible_rule_count

    # rules are defined as a bitarray whose value is the life/death of the neighbors defined by the n bit index


sys.modules[__name__] = A261864()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A261864()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=3600, quit_on_alert=True):
        print(f"{n} {val}")
