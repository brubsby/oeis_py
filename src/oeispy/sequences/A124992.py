import itertools
import logging
import math
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A124992(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[29, 70326806362093, 43, 127, 59221, 113, 32411, 71, 4957, 74509, 4271, 19013, 239, 2003, 463, 421, 613575503674084673, 32089, 211, 54601, 3109], start_index=1)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(29)
        q = math.prod(self(k) for k in range(1, n))
        r = q * 7
        val = (pow(r, 7) - 1)//(r - 1)
        for prime_factor in factor.generate_factors_by_size(val):
            if gmpy2.is_congruent(prime_factor, 1, 7):
                return prime_factor


sys.modules[__name__] = A124992()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A124992()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
