import itertools
import logging
import sys

import sympy

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A000041(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0)

    def calculate(self, n):
        return sympy.functions.combinatorial.numbers.partition(n)


sys.modules[__name__] = A000041()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A000041()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
