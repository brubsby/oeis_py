import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A227173(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[7, 13, 2371, 2791, 2999, 4621, 8819, 21563], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else gmpy2.mpz(1), n=n)
        term1 = pow(138, k-1)
        term2 = pow(137, k-1)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n)
            term1 *= 138
            term2 *= 137
            val = term1 + term2
            if gmpy2.is_divisible(val, 275):
                if prime.is_prime(val//275, care_probable=True):
                    self.delete_checkpoint(n=n)
                    return k


sys.modules[__name__] = A227173()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A227173()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
