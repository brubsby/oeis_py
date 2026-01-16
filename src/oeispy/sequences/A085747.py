import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A085747(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=False)

    def calculate(self, n):
        fac = gmpy2.fac(n)
        logging.debug(fac)
        for k in itertools.count(start=1):
            if semiprime.is_semi(fac + k) > 0:
                return k


sys.modules[__name__] = A085747()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A085747()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
