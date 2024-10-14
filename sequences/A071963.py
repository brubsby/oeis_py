import itertools
import logging
import sys
import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence
from sequences import A000041


class A071963(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0, b_file_lookup=True)

    def calculate(self, n):
        if n < 2:
            return gmpy2.mpz(1)
        return factor.biggest_prime_factor(A000041(n))


sys.modules[__name__] = A071963()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A071963()
    seq.generate_b_file(term_cpu_time=30, max_n=100000)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
