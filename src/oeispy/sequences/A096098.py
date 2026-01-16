import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A096098(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True, b_file_lookup=True)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(2)
        if n == 2:
            return gmpy2.mpz(1)
        previous_values = [self(k) for k in range(1, n)]
        concatenation = gmpy2.mpz("".join(map(str, previous_values)))
        divisors = factor.proper_divisors(concatenation)
        divisors = list(filter(lambda divisor: divisor not in previous_values, divisors))
        return divisors[0] #if len(divisors) else


sys.modules[__name__] = A096098()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A096098()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
