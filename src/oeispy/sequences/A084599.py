import itertools
import logging
import math
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A084599(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(2)
        if n == 2:
            return gmpy2.mpz(3)
        return factor.biggest_prime_factor(math.prod(self(k) for k in range(1, n)) - 1)


sys.modules[__name__] = A084599()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A084599()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
