import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A065447(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(1)
        return gmpy2.mpz(str(self(n-1)) + n * ("0" if gmpy2.is_even(n) else "1"))


sys.modules[__name__] = A065447()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A065447()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
