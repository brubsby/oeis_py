import itertools
import sys
import logging

import gmpy2

from oeispy.utils import semiprime
from oeispy.core import Sequence


class A082869(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[4, 7, 9, 13, 19, 23, 37, 71, 89, 97, 131, 167, 193, 227, 229, 257, 263, 269, 271], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        two = gmpy2.mpz(2)
        three = gmpy2.mpz(3)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n)
            k = gmpy2.mpz(k)
            val = pow(three, k) - pow(two, k)
            is_semi = semiprime.is_semi(val)
            if is_semi in [1, 2]:
                self.delete_checkpoint(n=n)
                return k
            if is_semi in [-1]:
                logging.info(f"yafu time, k={k}: http://factordb.com/index.php?query={val}")
                exit(1)


sys.modules[__name__] = A082869()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A082869().enumerate():
        print(f"{n} {val}")
