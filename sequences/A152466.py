import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A152466(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True, b_file_lookup=True)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(252)
        last = self(n-1)
        return last * factor.smallest_prime_factor(last + 1)


sys.modules[__name__] = A152466()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A152466()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
