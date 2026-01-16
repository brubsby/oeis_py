import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence

from sequences import A242175


class A242116(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = A242175(n)
        return k * pow(2, k) + 1


sys.modules[__name__] = A242116()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A242116()
    # print(seq.generate_data_section())
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
