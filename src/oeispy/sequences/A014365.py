import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A014365(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0, iterative_lookup=True, b_file_lookup=True)

    def calculate(self, n):
        if n == 0:
            return 1134
        return factor.aliquot_sum(self(n-1))


sys.modules[__name__] = A014365()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A014365()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
