import itertools
import logging
import sys
import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A000120(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        return gmpy2.bit_count(n)


sys.modules[__name__] = A000120()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A000120()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
