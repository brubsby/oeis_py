import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence
from sequences import A007942


class A361624(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        return factor.little_omega(A007942(n))


sys.modules[__name__] = A361624()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A361624()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
