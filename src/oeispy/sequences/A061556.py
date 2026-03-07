import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A061556(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[],
                         start_index=0)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        k_fac = gmpy2.fac(k-1)
        rhs = n * k_fac
        factors = factor.factorize(k_fac)
        _ = gmpy2.mpz(2)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n)
            rhs *= k
            factors.extend(factor.factorize(k))
            if factor.sigma(_, factors=factors) >= rhs:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A061556()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A061556()
    # seq.generate_b_file(cpu_term_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
