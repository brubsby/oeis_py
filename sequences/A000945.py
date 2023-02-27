import itertools
import logging
import math
import sys

import gmpy2

import modules.factor as factor
from sequence import Sequence


class A000945(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True, iterative_lookup=True)

    def calculate(self, n):
        assert n > 0
        if n == 1:
            return gmpy2.mpz(2)
        return factor.smallest_prime_factor(math.prod(self(k) for k in range(1, n)) + 1)



sys.modules[__name__] = A000945()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A000945()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
