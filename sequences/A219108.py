import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A219108(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[0, 1, 3, 5, 17, 59, 101, 563, 2617, 9299, 22109, 132989, 364979, 1970869, 23515229, 109258049, 831731339], start_index=0)

    def calculate(self, n):
        k = self.load_checkpoint(default=0, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 50000, n=n)
            if factor.little_omega(pow(k, 3) + 1) == n:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A219108()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A219108()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
