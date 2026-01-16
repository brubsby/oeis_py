import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A096723(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(1)
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else gmpy2.mpz(1), n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n)
            val = pow(gmpy2.mpz(3), k) + pow(-1, n)
            if gmpy2.is_even(val):
                val = val // 2
                if prime.is_prime(val, check_factor_db=True):
                    self.delete_checkpoint(n=n)
                    return k


sys.modules[__name__] = A096723()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A096723()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
