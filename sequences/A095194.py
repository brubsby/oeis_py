import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A095194(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        facstr = gmpy2.fac(n).digits()
        for k in itertools.count(start=0):
            val = gmpy2.mpz(facstr + str(k))
            if semiprime.is_semi(val) > 0:
                return k


sys.modules[__name__] = A095194()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A095194()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
