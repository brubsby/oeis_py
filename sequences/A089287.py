import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence

from sequences import A001414, A011545


class A089287(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0, b_file_lookup=True)

    def calculate(self, n):
        return A001414(A011545(n))


sys.modules[__name__] = A089287()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A089287()
    print(seq.generate_data_section())
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
