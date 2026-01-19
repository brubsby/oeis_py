import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence

from oeispy.sequences import A000295


class A099441(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self(n-1)+1 if n > 1 else 1
        for k in itertools.count(start=k):
            if semiprime.is_semi(A000295(k)) > 0:
                return k


sys.modules[__name__] = A099441()

if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    seq = A099441()
    # seq.generate_data_section()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
