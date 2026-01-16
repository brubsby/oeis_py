import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence
from sequences import A104365


class A104368(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        return len(factor.distinct_factors(A104365(n), threads=8))


sys.modules[__name__] = A104368()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A104368()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
