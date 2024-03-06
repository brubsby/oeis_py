import itertools
import logging
import math
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A124985(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[7, 23, 207367, 1902391, 167, 1511, 28031, 79, 3142977463, 2473230126937097422987916357409859838765327, 2499581669222318172005765848188928913768594409919797075052820591, 223], start_index=1)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(7)
        q = math.prod(self(k) for k in range(1, n))
        val = 8 * pow(q, 2) - 1
        for prime_factor in factor.generate_factors_by_size(val):
            if gmpy2.is_congruent(prime_factor, 7, 8):
                return prime_factor


sys.modules[__name__] = A124985()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A124985()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
