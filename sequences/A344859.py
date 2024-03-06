import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A344859(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0)

    def calculate(self, n):
        return factor.number_of_divisors(pow(gmpy2.mpz(n), gmpy2.mpz(n)) + 1)


sys.modules[__name__] = A344859()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A344859()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
