import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A008352(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0, iterative_lookup=True)

    def calculate(self, n):
        if n == 0:
            return gmpy2.mpz(1)
        if n == 1:
            return gmpy2.mpz(2)
        return gmpy2.mpz(gmpy2.digits(self(n-2)) + gmpy2.digits(self(n-1)))



sys.modules[__name__] = A008352()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A008352()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
