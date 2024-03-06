import itertools
import logging
import math
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A102926(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(2)
        if n == 2:
            return gmpy2.mpz(3)
        val = math.prod(self(k) for k in range(1, n))
        return min(factor.smallest_prime_factor(val-1), factor.smallest_prime_factor(val+1))


sys.modules[__name__] = A102926()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A102926()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
