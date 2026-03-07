import itertools
import logging
import sys

import gmpy2
import primesieve

from oeispy.utils import factor, base, prime, semiprime, primorial
from oeispy.core import Sequence


class A034386(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0)

    def calculate(self, n):
        return primorial.primorial(n)

    def generator(self, start):
        n = start
        if n == 0:
            yield 1
            n = 1
        val = primorial.primorial(n-1)
        prime_it = primesieve.Iterator()
        prime_it.skipto(n+1)
        p = prime_it.prev_prime()
        if p == n:
            val *= p
            yield val
            n += 1
        p = prime_it.next_prime()
        for n in itertools.count(start=n):
            if n == p:
                val *= p
                p = prime_it.next_prime()
            yield val


sys.modules[__name__] = A034386()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A034386()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
        if n > 20:
            exit()
