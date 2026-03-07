import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A274700(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        term = 7 * pow(10, k)
        for k in itertools.count(start=k):
            val = term + 37
            if k % 2 == 0:
                term *= 10
                continue
            self.checkpoint(k, k, 1, n=n)
            if prime.is_prime(val):
                self.delete_checkpoint(n=n)
                return k
            term *= 10


sys.modules[__name__] = A274700()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A274700()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
