import itertools
import logging
import sys

import primesieve

from modules import factor, base, prime, semiprime
from sequence import Sequence
from sequences import A002110


# Euclid Number
class A006862(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0)

    def generator(self, start):
        prod = A002110(start)
        for p in prime.generator(start+1, start_nth=True):
            yield prod + 1
            prod *= p


sys.modules[__name__] = A006862()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A006862()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True, start=0):
        if n > 20:
            break
        print(f"{n} {val}")
