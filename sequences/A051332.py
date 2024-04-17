import itertools
import logging
import math
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A051332(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(65537)
        return factor.smallest_prime_factor(math.prod(self(k) for k in range(1, n)) + 1, digit_limit=10)


sys.modules[__name__] = A051332()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A051332()
    # print(seq.generate_data_section())
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
