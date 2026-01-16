import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence
from sequences import A006530, A002110, A000040

class A065316(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=3, b_file_lookup=True)

    def calculate(self, n):
        return A006530(A002110(n)-A000040(n+1))


sys.modules[__name__] = A065316()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A065316()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
