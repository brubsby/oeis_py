import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence
from sequences import A019520


class A105388(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        return factor.number_of_divisors(A019520(n), threads=8)


sys.modules[__name__] = A105388()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A105388()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
