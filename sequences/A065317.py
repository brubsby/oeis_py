import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence
from sequences import A006530, A002110, A000040

class A065317(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        return A006530(A002110(n)+A000040(n+1))


sys.modules[__name__] = A065317()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A065317()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
