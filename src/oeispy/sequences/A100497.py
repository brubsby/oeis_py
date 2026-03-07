import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A100497(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else gmpy2.mpz(0), n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n, cooldown=None)
            val = pow(pow(gmpy2.mpz(2), k) + 1, gmpy2.mpz(4)) - 2
            if semiprime.is_semi(val, threads=4) in [1, 2]:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A100497()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A100497()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
