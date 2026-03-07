import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence
from oeispy.sequences import A000720


class A276650(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        prev = self(n-1) if n > 1 else -1
        for n, p in enumerate(prime.generator(start=1, start_nth=True), start=1):
            val = pow(p, n) - A000720(n)
            if val <= prev:
                continue
            if prime.is_prime(val):
                self.delete_checkpoint(n)
                return val
            self.checkpoint(n, n, 100)


sys.modules[__name__] = A276650()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A276650()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
