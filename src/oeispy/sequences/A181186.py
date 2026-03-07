import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A181186(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        return len(factor.factorize((pow(2, n)-1) * gmpy2.fac(n)+1, threads=8))


sys.modules[__name__] = A181186()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A181186()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
