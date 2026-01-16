import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence

import A000040


class A177996(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=3, b_file_lookup=True)

    def calculate(self, n):
        p = A000040(n)
        for prime_factor in factor.generate_factors_by_size(pow(p-1, p)+1):
            if prime_factor != p:
                return prime_factor


sys.modules[__name__] = A177996()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A177996()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
