import itertools
import logging
import math
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A217759(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(3)
        q = math.prod(self(k) for k in range(1, n))
        val = 4 * pow(q, 2) - 1
        for prime_factor in factor.generate_factors_by_size(val):
            if gmpy2.is_congruent(prime_factor, 3, 4):
                return prime_factor


sys.modules[__name__] = A217759()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A217759()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
