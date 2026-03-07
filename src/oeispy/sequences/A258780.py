import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A258780(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=2)

    def calculate(self, n):
        twoton = pow(2, n)
        for k in itertools.count(start=1):
            k2 = k * k
            val = k2 + 1
            if semiprime.is_semi(val):
                factors = factor.factorize(val)
                numerator = factors[1] - factors[0]
                if gmpy2.is_divisible(numerator, twoton):
                    if prime.is_prime(numerator//twoton):
                        return k


sys.modules[__name__] = A258780()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A258780()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
