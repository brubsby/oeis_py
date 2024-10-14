import itertools
import sys
import logging

import gmpy2

from modules import semiprime, prime
from sequence import Sequence


class A089485(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=(self(n-1)-1)//2+1 if n > 1 else 1, n=n)
        two = gmpy2.mpz(2)
        four = gmpy2.mpz(4)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n, cooldown=5)
            k = gmpy2.mpz(k)
            m = k * 2 + 1
            # val = pow(m, four) + pow(four, m)
            is_semi = prime.is_prime(
                abs(pow(m, two) + m * pow(two, k + 1) + pow(two, m))) and prime.is_prime(
                abs(pow(m, two) - m * pow(two, k + 1) + pow(two, m)))
            # is_semi = semiprime.is_semi(val)
            if is_semi:
                self.delete_checkpoint(n=n)
                return m


sys.modules[__name__] = A089485()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A089485().enumerate(alert_time=10, quit_on_alert=True):
        print(f"{n} {val}")
