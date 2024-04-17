import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A080208(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 1, 1, 1, 1, 8, 95, 31, 85, 59, 1078, 754, 311, 3508, 1828, 49957, 22844], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=gmpy2.mpz(1), n=n)
        pow2 = pow(2, n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 1, n=n)
            val = pow(k+1, pow2) + pow(k, pow2)
            if prime.is_prime(val):
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A080208()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A080208()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
