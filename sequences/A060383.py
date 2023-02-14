import itertools
import sys
import logging

import gmpy2
import primesieve

from modules import factor, prime
from sequence import Sequence


class A060383(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)
        self.divisors = primesieve.primes(2, int(1e6))

    def calculate(self, n):
        return factor.smallest_prime_factor(gmpy2.fib(n), divisors=self.divisors, digit_limit=10)


sys.modules[__name__] = A060383()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A060383().enumerate():
        print(f"{n} {val}")
