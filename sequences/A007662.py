import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A007662(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 1, 2, 3], start_index=0, iterative_lookup=True)

    def calculate(self, n):
        return n * self(n-4)


sys.modules[__name__] = A007662()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A007662()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
        if n > 100:
            break
