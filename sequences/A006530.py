import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A006530(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        if n == 1:
            return 1
        return factor.biggest_prime_factor(n)


sys.modules[__name__] = A006530()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A006530()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
        if n > 100:
            break
