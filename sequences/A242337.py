import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A242337(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 18, 22, 23, 25, 32, 35, 38, 45, 51, 54, 57, 68, 72, 82, 97, 110, 138, 155, 234, 254], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else gmpy2.mpz(1), n=n)
        pow6 = pow(gmpy2.mpz(6), k-1)
        for k in itertools.count(start=k):
            pow6 *= 6
            val = k * pow6 - 1
            if semiprime.is_semi(val, run_yafu=True, check_factor_db_prime=False, threads=1) in [1, 2]:
                self.delete_checkpoint(n=n)
                return k
            self.checkpoint(k, k, n=n, cooldown=None)


sys.modules[__name__] = A242337()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A242337()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
