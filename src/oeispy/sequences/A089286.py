import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence

from oeispy.sequences import A008472, A011545


class A089286(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0, b_file_lookup=True)

    def calculate(self, n):
        return A008472(A011545(n))


sys.modules[__name__] = A089286()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A089286()
    print(seq.generate_data_section())
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
