import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence
from sympy import harmonic


class A001008(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        return harmonic(n).numerator


sys.modules[__name__] = A001008()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A001008()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
