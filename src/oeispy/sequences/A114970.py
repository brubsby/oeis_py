import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A114970(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        k = self(n-1)+1 if n > 1 else 1
        for k in itertools.count(start=k):
            if semiprime.is_semi(pow(2, k) + pow(k, 2)) > 0:
                return k


sys.modules[__name__] = A114970()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A114970()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
