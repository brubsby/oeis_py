import itertools
import logging
import sys

import gmpy2
import primesieve

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence

from sympy import primorial


class A007504(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0)

    def calculate(self, n):
        return sum(primesieve.n_primes(n), gmpy2.mpz()) if n > 0 else gmpy2.mpz(0)

    def generator(self, start):
        value = self.calculate(start) if start > 0 else gmpy2.mpz(0)
        nth_prime = primesieve.nth_prime(start) if start > 0 else 1
        prime_it = primesieve.Iterator()
        prime_it.skipto(nth_prime)
        yield value
        while True:
            value += prime_it.next_prime()
            yield value



sys.modules[__name__] = A007504()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A007504()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        if n > 100:
            break
        print(f"{n} {val}")
