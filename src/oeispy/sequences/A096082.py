import itertools
import logging
import sys
import gmpy2
import primesieve
from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A096082(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        p = self.load_checkpoint(default=3, n=n)
        for k, p in enumerate(prime.generator(p)):
            p = gmpy2.mpz(p)
            self.checkpoint(p, k, 10000000, n=n)
            p2 = p * p
            if gmpy2.powmod(gmpy2.mpz(n), p - 1, p2) == 1:
                self.delete_checkpoint(n=n)
                return p


sys.modules[__name__] = A096082()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A096082()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
