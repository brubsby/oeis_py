import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A019520(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True)

    def calculate(self, n):
        if n == 1:
            return "2"
        return self(n-1) + str(n*2)


sys.modules[__name__] = A019520()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A019520()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        if n > 100:
            break
        print(f"{n} {val}")
