import itertools
import logging
import sys

import primesieve
import math
import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A999999(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True, b_file_lookup=True)

    def calculate(self, n):
        k = 8
        if n <= k:
            prev = list(primesieve.n_primes(k))
            return prev[n-1]
        prev = self.list(n-1, start=n-k)
        val = math.prod(prev) + 1
        return factor.smallest_prime_factor(val, check_factor_db=True, threads=16, digit_limit=0)


sys.modules[__name__] = A999999()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A999999()
    seq.generate_b_file(max_n=171772, term_digit_length_limit=None)
    # for n, val in seq.enumerate():
    #     print(f"{val},")
