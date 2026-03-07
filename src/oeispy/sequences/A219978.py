import itertools
import sys
import logging

import gmpy2

from oeispy.utils import semiprime
from oeispy.core import Sequence


class A219978(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[5, 6, 13, 16, 18, 21, 22, 28, 29, 37, 46, 60, 71, 84], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n)
            k = gmpy2.mpz(k)
            val = pow(k, k) - pow(k - 1, k - 1)
            is_semi = semiprime.is_semi(val)
            if is_semi in [1, 2]:
                self.delete_checkpoint(n=n)
                return k
            if is_semi in [-1]:
                logging.info(f"yafu time, k={k}: http://factordb.com/index.php?query={val}")
                exit(1)


sys.modules[__name__] = A219978()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A219978().enumerate(alert_time=30, quit_on_alert=True):
        print(f"{n} {val}")
