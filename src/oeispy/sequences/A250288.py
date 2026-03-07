import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A250288(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self(n-1) + 1 if n > 1 else 1
        for k in itertools.count(start=k):
            val = (pow(12, k) - 1)//11
            if semiprime.is_semi(val):
                return k


sys.modules[__name__] = A250288()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A250288()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
