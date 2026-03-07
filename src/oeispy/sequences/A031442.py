import itertools
import logging
import sys

import gmpy2
import primesieve

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A031442(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0, b_file_lookup=True)

    def calculate(self, n):
        if n == 0:
            return gmpy2.mpz(13)
        return factor.biggest_prime_factor(prime.previous_prime(self(n-1))*self(n-1)-1)


sys.modules[__name__] = A031442()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A031442()
    print(seq.generate_data_section())
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
