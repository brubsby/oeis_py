import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence
from oeispy.sequences import A011545, A006530


class A078604(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0, b_file_lookup=True)

    def calculate(self, n):
        return factor.biggest_prime_factor(A011545(n), threads=12)


sys.modules[__name__] = A078604()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A078604()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
