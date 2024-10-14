import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A020639(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        if n == 1:
            return 1
        return factor.smallest_prime_factor(n, digit_limit=1)



sys.modules[__name__] = A020639()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A020639()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
        if n > 100:
            break
