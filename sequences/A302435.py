import itertools
import logging
import sys

import primesieve
import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A302435(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        limit = pow(10, n)
        count = 0
        for b in range(0, limit+1):
            if gmpy2.is_prime(b*b+3):
                count += 1
        return count


sys.modules[__name__] = A302435()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A302435()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
