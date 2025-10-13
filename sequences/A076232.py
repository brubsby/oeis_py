import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence
from sequences import A001223, A000142


class A076232(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        return A001223(A000142(n))


sys.modules[__name__] = A076232()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A076232()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
