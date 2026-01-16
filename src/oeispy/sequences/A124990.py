import itertools
import logging
import math
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A124990(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[13, 28393, 128758492789, 73, 193, 37, 457, 8363172060732903211423577787181], start_index=1)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(13)
        q = math.prod(self(k) for k in range(1, n))
        val = (pow(q, 4) - pow(q, 2) + 1)
        for prime_factor in factor.generate_factors_by_size(val):
            return prime_factor


sys.modules[__name__] = A124990()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A124990()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
