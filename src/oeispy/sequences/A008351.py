import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence

import gmpy2


class A008351(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(1)
        if n == 2:
            return gmpy2.mpz(2)
        return gmpy2.mpz(str(self(n-1)) + str(self(n-2)))


sys.modules[__name__] = A008351()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A008351()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
        if n > 100:
            break
