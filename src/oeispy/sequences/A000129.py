import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A000129(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0, iterative_lookup=True)

    def calculate(self, n):
        if n == 0:
            return gmpy2.mpz(0)
        if n == 1:
            return gmpy2.mpz(1)
        return 2 * self(n-1) + self(n-2)


sys.modules[__name__] = A000129()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A000129()
    print(seq.generate_data_section())
    # seq.generate_b_file(term_cpu_time=30)
    # for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
    #     print(f"{n} {val}")
