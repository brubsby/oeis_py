import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A046798(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0)

    def calculate(self, n):
        return factor.number_of_divisors(pow(2, n) + 1)


sys.modules[__name__] = A046798()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A046798()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
