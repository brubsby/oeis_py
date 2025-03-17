import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A001414(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        return sum(factor.factorize(n))


sys.modules[__name__] = A001414()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A001414()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
        if n > 100:
            break
