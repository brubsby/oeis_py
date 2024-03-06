import itertools
import logging
import math
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A124991(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(11)
        q = math.prod(self(k) for k in range(1, n))
        r = q * 5
        val = (pow(r, 5) - 1)//(r - 1)
        for prime_factor in factor.generate_factors_by_size(val):
            if gmpy2.is_congruent(prime_factor, 1, 5):
                return prime_factor


sys.modules[__name__] = A124991()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A124991()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
