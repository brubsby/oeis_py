import itertools
import logging
import sys

import gmpy2
import primesieve
import sympy

from modules import factor, base, prime, semiprime, primorial
from sequence import Sequence


class A002110(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0)

    def calculate(self, n):
        return primorial.nth_primorial(n)

    def generator(self, start):
        value = self(start) if start > 1 else gmpy2.mpz(1)
        nth_prime = primesieve.nth_prime(start) if start > 0 else 1
        prime_it = primesieve.Iterator()
        prime_it.skipto(nth_prime)
        yield value
        while True:
            value *= prime_it.next_prime()
            yield value


sys.modules[__name__] = A002110()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A002110()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        if n > 100:
            break
        print(f"{n} {val}")
