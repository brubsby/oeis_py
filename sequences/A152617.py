import cProfile
import copy
import itertools
import logging
import math
import sys
import heapq
import gmpy2

import primesieve

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A152617(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[2, 6, 60, 1140, 22230, 778050, 28787850, 1237877550, 82937795850, 6054459097050, 802693813972050, 126022928793611850], start_index=1)

    def calculate(self, n):
        n = gmpy2.mpz(n)
        counter = 0
        seen_sigma = set()
        for m, factors in factor.numbers_with_n_distinct_factors_generator(n):
            counter += 1
            self.checkpoint(m, counter, 10000, n=n, total=True)
            sigma = factor.sigma(m, factors=factors)
            if sigma in seen_sigma:
                continue
            if len(factor.distinct_factors(sigma)) == n:
                self.delete_checkpoint(n=n)
                return m
            seen_sigma.add(sigma)





sys.modules[__name__] = A152617()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A152617()
    # seq.generate_b_file(term_cpu_time=30)
#     cProfile.run("""
# import A152617
# A152617(10)
#     """)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
