import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A143665(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 100000, n=n)
            if k == 0:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A143665()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A143665()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
