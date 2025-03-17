import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A252657(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self(n-1) + 1 if n > 1 else 1
        for k in itertools.count(start=k):
            val = (pow(4, k) - k)
            if semiprime.is_semi(val):
                return k


sys.modules[__name__] = A252657()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A252657()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
