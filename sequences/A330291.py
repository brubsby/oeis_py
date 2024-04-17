import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A330291(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        if n == 1 or n == 2:
            return 1
        prevlist = self.list(n-1)
        k = base.concat(prevlist)
        for p in factor.smallest_prime_factor_generator(k):
            if p not in prevlist:
                return p


sys.modules[__name__] = A330291()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A330291()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
