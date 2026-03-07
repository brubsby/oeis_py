import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A242341(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 6, 20, 29, 35, 40, 79, 164, 185, 198, 201, 218, 248, 249, 251, 264, 267, 274, 305, 323, 339, 344, 350, 362, 432, 539], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else gmpy2.mpz(1), n=n)
        pow10 = pow(gmpy2.mpz(10), k-1)
        for k in itertools.count(start=k):
            pow10 *= 10
            val = k * pow10 - 1
            if semiprime.is_semi(val, run_yafu=True, check_factor_db_prime=False, threads=1) in [1, 2]:
                self.delete_checkpoint(n=n)
                return k
            self.checkpoint(k, k, n=n, cooldown=None)


sys.modules[__name__] = A242341()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A242341()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
