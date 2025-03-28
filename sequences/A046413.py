import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence

from sequences import A000042


class A046413(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self(n-1) + 1 if n > 1 else 1
        for k in itertools.count(start=k):
            if semiprime.is_semi(A000042(k)) > 0:
                return k


sys.modules[__name__] = A046413()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A046413()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
