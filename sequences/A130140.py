import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence

from sequences import T000001


class A130140(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0)

    def calculate(self, n):
        if n == 0:
            return gmpy2.mpz(1)
        value = 2 * n + 1
        count = 0
        while not prime.is_prime(value):
            count += 1
            logging.info((f"{count} applications"))
            value = T000001(value)
            logging.info(f"{value}")
        return value


sys.modules[__name__] = A130140()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A130140()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
