import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence
from oeispy.sequences import A000040


class A001223(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        val = A000040(n+1)
        return val-prime.previous_prime(val)


sys.modules[__name__] = A001223()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A001223()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
        if n > 100:
            break
