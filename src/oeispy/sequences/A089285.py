import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence

from sequences import A000203, A011545


class A089285(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0, b_file_lookup=True)

    def calculate(self, n):
        return A000203(A011545(n))


sys.modules[__name__] = A089285()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A089285()
    print(seq.generate_data_section())
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
