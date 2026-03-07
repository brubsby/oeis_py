import itertools
import logging
import math
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A124993(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[23, 4847239, 2971, 3936923, 9461, 1453, 331, 81373909, 89, 920771904664817214817542307, 353, 401743, 17088192002665532981, 11617], start_index=1)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(23)
        q = math.prod(self(k) for k in range(1, n))
        r = q * 11
        val = (pow(r, 11) - 1)//(r - 1)
        for prime_factor in factor.generate_factors_by_size(val):
            if gmpy2.is_congruent(prime_factor, 1, 11):
                return prime_factor


sys.modules[__name__] = A124993()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A124993()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
