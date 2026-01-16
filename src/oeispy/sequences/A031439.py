import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A031439(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0)

    def calculate(self, n):
        if n == 0:
            return gmpy2.mpz(1)
        return factor.biggest_prime_factor(pow(self(n-1), 2) + 1)


sys.modules[__name__] = A031439()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A031439()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
