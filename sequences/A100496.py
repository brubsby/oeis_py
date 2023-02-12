import itertools
import sys
import logging

import gmpy2

from modules import primetest
from sequence import Sequence


class A100496(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 7, 25, 31, 34, 271, 514, 2896, 8827, 16816, 37933], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n)
            val = pow(pow(gmpy2.mpz(2), k) + 1, 4) - 2
            if primetest.is_prime(val):
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A100496()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A100496().enumerate( alert_time=10, quit_on_alert=True):
        print(f"{n} {val}")
