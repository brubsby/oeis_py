import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A268110(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[3, 4, 6, 9, 10, 15, 19, 22, 26, 34, 47, 55, 67, 69, 72, 92, 100, 117, 160, 169, 268, 278], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else gmpy2.mpz(1), n=n)
        pow2 = pow(gmpy2.mpz(2), k-1)
        for k in itertools.count(start=k):
            pow2 *= 2
            val = (pow2 - k + 1) * pow2 + 1
            if semiprime.is_semi(val, run_yafu=True, check_factor_db_prime=False, threads=4) in [1, 2]:
                self.delete_checkpoint(n=n)
                return k
            self.checkpoint(k, k, n=n, cooldown=None)


sys.modules[__name__] = A268110()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A268110()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
