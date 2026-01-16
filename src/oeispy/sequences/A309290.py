import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A309290(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = (self(n-1) + 1) if n > 1 else 0
        for k in itertools.count(start=k):
            k2 = k * k
            val = gmpy2.bincoef(k2, k) - k2
            if factor.is_squarefree(val):
                return k


sys.modules[__name__] = A309290()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A309290()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
