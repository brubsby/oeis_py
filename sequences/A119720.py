import itertools
import sys
import logging

import gmpy2

from modules import semiprime
from sequence import Sequence


class A119720(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 2, 6, 9, 12, 14, 26, 33, 44, 54, 126, 141, 830, 2436, 3534, 3846, 4152, 4460, 4974, 13160, 13200, 13832, 21996, 28065], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        seven = gmpy2.mpz(7)
        term = pow(seven, k)
        for k in itertools.count(start=k):
            val = term + 2
            self.checkpoint(k, k, n=n)
            is_semi = semiprime.is_semi(val)
            if is_semi in [1, 2]:
                self.delete_checkpoint(n=n)
                return k
            if is_semi in [-1]:
                logging.info(f"yafu time, k={k}: http://factordb.com/index.php?query={val}")
                exit(1)
            term *= seven


sys.modules[__name__] = A119720()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A119720().enumerate(alert_time=10, quit_on_alert=True):
        print(f"{n} {val}")
