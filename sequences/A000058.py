import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A000058(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0, iterative_lookup=True)

    def calculate(self, n):
        if n == 0:
            return gmpy2.mpz(2)
        return pow(self(n-1), 2) - self(n-1) + 1


sys.modules[__name__] = A000058()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A000058()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        if n > 10:
            break
        print(f"{n} {val}")
