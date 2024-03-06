import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence
import A104357


class A104363(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=2)

    def calculate(self, n):
        return factor.totient(A104357(n))


sys.modules[__name__] = A104363()
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("")
    seq = A104363()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
