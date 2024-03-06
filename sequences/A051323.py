import itertools
import logging
import math
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A051323(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(67)
        return factor.smallest_prime_factor(math.prod(self(k) for k in range(1, n)) + 1, digit_limit=1)


sys.modules[__name__] = A051323()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A051323()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
