import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A155886(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 3, 14, 11, 6, 1941491, 10, 83, 31, 13, 123, 35, 71, 27, 34913, 241, 18, 8059, 34, 349, 44, 25, 39, 100867561, 76, 231, 253, 66203, 57, 227, 139, 45, 184, 37, 111, 97, 55, 41, 103, 1099, 81, 66791, 53], start_index=0)

    def calculate(self, n):
        k = self.load_checkpoint(default=1, n=n)
        val = pow(gmpy2.mpz(2), k-1)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 100000, n=n)
            val *= 2
            if gmpy2.powmod(2, val, k) == n:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A155886()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A155886()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
