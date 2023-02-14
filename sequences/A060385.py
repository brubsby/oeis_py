import itertools
import sys
import logging

import gmpy2

from modules import factor
from sequence import Sequence


class A060385(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=3, b_file_lookup=True)

    def calculate(self, n):
        return factor.biggest_prime_factor(gmpy2.fib(n))


sys.modules[__name__] = A060385()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A060385()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate():
        print(f"{n} {val}")
