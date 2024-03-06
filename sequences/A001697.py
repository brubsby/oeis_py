import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A001697(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0, iterative_lookup=True)

    def calculate(self, n):
        if n == 0:
            return gmpy2.mpz(1)
        k = gmpy2.mpz(0)
        for i in range(n):
            k += self(i)
        return self(n-1) * k


sys.modules[__name__] = A001697()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A001697()
    seq.generate_b_file(term_cpu_time=30)
    print(seq.generate_data_section())
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
        if n == 9:
            quit(0)
