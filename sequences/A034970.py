import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A034970(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0)

    def calculate(self, n):
        if n == 0:
            return 2
        if n == 1:
            return 3
        return factor.biggest_prime_factor(self(n-2)*self(n-1)-1)


sys.modules[__name__] = A034970()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A034970()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
