import itertools
import math
import sys
import logging

import gmpy2
import primesieve

from modules import prime
from sequence import Sequence


class A139439(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 2, 3, 4, 7, 18, 21, 70, 76, 323, 340, 556, 572, 3433, 5457, 5897, 10820], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        primes = primesieve.n_primes(k)
        p = primes[-1]
        prim = math.prod(gmpy2.mpz(prime) for prime in primes)
        it = primesieve.Iterator()
        it.skipto(p)
        for k in itertools.count(start=k):
            val = prim // 2 + 4
            self.checkpoint(k, k, n=n)
            if prime.is_prime(val):
                self.delete_checkpoint(n=n)
                return k
            p = it.next_prime()
            prim *= p



sys.modules[__name__] = A139439()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A139439().enumerate():
        print(f"{n} {val}")
