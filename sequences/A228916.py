import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence
from sequences import A108300


class A228916(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 3, 9, 15, 39, 225, 231, 363, 687, 1299, 1335, 1809, 2367, 12735], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 1, n=n)
            if prime.is_prime(A108300(k)):
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A228916()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A228916()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
