import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A050244(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[3, 6, 7, 8, 10, 11, 12, 14, 16, 22, 32, 34, 38, 82, 83, 106, 128, 149, 218, 223, 334, 412, 436, 599, 647, 916, 1373, 4414, 7246, 8423, 10118, 10942, 15898, 42422 ], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else gmpy2.mpz(1), n=n)
        pow2 = pow(gmpy2.mpz(2), k-1)
        pow3 = pow(gmpy2.mpz(3), k-1)
        for k in itertools.count(start=k):
            pow2 *= 2
            pow3 *= 3
            val = pow2 + pow3
            # yafu hangs on composites this big
            if semiprime.is_semi(val, run_yafu=False) in [1, 2]:
                self.delete_checkpoint(n=n)
                return k
            self.checkpoint(k, k, n=n, cooldown=None)


sys.modules[__name__] = A050244()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A050244()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
