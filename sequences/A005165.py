import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A005165(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0, iterative_lookup=True)

    def calculate(self, n):
        if n == 0:
            return gmpy2.mpz(0)
        return gmpy2.fac(n) - self(n-1)


sys.modules[__name__] = A005165()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A005165()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
