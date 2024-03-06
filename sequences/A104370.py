import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence
from sequences import A104365


class A104370(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        val = A104365(n)
        return sum(factor.proper_divisors(val, threads=8)) + 1 + val


sys.modules[__name__] = A104370()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A104370()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
