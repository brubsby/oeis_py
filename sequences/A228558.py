import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A228558(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[13, 61, 67, 107, 383, 647, 3571, 37967], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        term1 = pow(17,k)
        term2 = pow(4,k)
        for k in itertools.count(start=k):
            val = term1 + term2
            if gmpy2.is_divisible(val, 21) and prime.is_prime(val//21):
                self.delete_checkpoint(n=n)
                return k
            self.checkpoint(k, k, 1, n=n)
            term1 *= 17
            term2 *= 4


sys.modules[__name__] = A228558()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A228558()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
