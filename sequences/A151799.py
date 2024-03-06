import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A151799(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=3)

    def calculate(self, n):
        return prime.previous_prime(n)


sys.modules[__name__] = A151799()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A151799()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
