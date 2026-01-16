import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence

from sequences import A019520


class A108728(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[	1, 2, 3, 2, 5, 3, 2, 3, 6, 5, 3, 4, 6, 4, 5, 4, 3, 5, 4, 7, 6, 5, 8, 3, 7, 4, 4, 8, 5, 7, 4, 4, 8, 5, 7, 6, 4, 8, 8, 7, 5, 3, 7, 4, 6, 10, 11, 5, 4, 10, 6, 5, 6, 5, 5, 4, 9, 4, 8, 9, 6, 5, 8, 4, 12, 5, 4, 8, 10, 5, 9, 7], start_index=1)

    def calculate(self, n):
        return len(factor.distinct_factors(A019520(n), threads=16))


sys.modules[__name__] = A108728()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A108728()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=False):
        # print(f"{n} {val}")
        print(f"{val}", end=", ")
