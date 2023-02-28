import cProfile
import itertools
import sys
import logging

import gmpy2
import primesieve

from modules import prime, semiprime, factor, base
from sequence import Sequence

import A007504

#Let f denote the map that replaces k with the concatenation of its proper divisors, written in increasing order,
# each divisor being written in base 10 with its digits in reverse order.
class T000001(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True)

    def calculate(self, n):
        if n == 1 or prime.is_prime(n):
            return gmpy2.mpz(n)
        return gmpy2.mpz("".join([gmpy2.digits(divisor)[::-1] for divisor in sorted(factor.get_all_proper_divisors(n))]))



sys.modules[__name__] = T000001()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    [print(val, end=", ") for val in itertools.islice(T000001().generator(start=1), 20)]
    for n, val in T000001().enumerate():
        # print(f"{val}, ", end="")
        print(f"{n} {val}")
