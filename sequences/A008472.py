import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A008472(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        return sum(factor.distinct_factors(n))


sys.modules[__name__] = A008472()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A008472()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
        if n > 100:
            break
