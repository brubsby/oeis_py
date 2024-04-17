import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence

from sequences import A000217


class A078795(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True)

    def calculate(self, n):
        return (self(n-1) + str(A000217(n))) if n > 1 else "1"


sys.modules[__name__] = A078795()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A078795()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
