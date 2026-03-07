import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence
import A037279


class A130139(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 3, 5, 7, 3, 11, 13, 1129, 17, 19, 37, 23, 5, 313, 29, 31, 311, 1129, 37, 313, 41, 43], start_index=0)

    def calculate(self, n):
        if n == 0:
            return gmpy2.mpz(1)
        value = 2 * n + 1
        count = 0
        while not prime.is_prime(value):
            count += 1
            logging.info((f"{count} applications"))
            value = A037279(value)
        return value



sys.modules[__name__] = A130139()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A130139()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
