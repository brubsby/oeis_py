import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence

import A001358


class A109313(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        factors = factor.factorize(A001358(n))
        return abs(factors[0] - factors[1])


sys.modules[__name__] = A109313()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A109313()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
