import itertools
import logging
import math
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A125045(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(3)
        q = math.prod(self(k) for k in range(1, n))
        val = q + 2
        return factor.smallest_prime_factor(val)


sys.modules[__name__] = A125045()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A125045()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
