import itertools
import logging
import math
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A000946(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(2)
        prod = math.prod([self(k) for k in range(1, n)])
        return factor.biggest_prime_factor(1 + prod)



sys.modules[__name__] = A000946()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A000946()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
