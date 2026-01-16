import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence

from sequences import A001221, A000041, A000045


class A116087(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        return A001221(A000041(A000045(n)))


sys.modules[__name__] = A116087()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A116087()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
