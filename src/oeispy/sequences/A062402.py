import itertools
import logging
import sys

from sympy import divisor_sigma, totient
from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A062402(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        return divisor_sigma(totient(n))


sys.modules[__name__] = A062402()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A062402()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
