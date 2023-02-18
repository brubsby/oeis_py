import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A252789(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[7, 19, 39, 43, 87, 135, 147, 177, 223, 255, 403], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else gmpy2.mpz(1), n=n)
        pow4 = pow(gmpy2.mpz(4), k-1)
        for k in itertools.count(start=k):
            pow4 *= 4
            val = pow4 + k
            if semiprime.is_semi(val, run_yafu=True, check_factor_db_prime=False, threads=1) in [1, 2]:
                self.delete_checkpoint(n=n)
                return k
            self.checkpoint(k, k, n=n, cooldown=None)


sys.modules[__name__] = A252789()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A252789()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
