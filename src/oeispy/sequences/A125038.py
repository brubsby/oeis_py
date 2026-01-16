import logging
import math
import sys

import gmpy2

from oeispy.utils import factor
from oeispy.core import Sequence


class A125038(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[103, 307, 9929, 187095201191, 76943, 37061, 137, 5615258941637, 302125531, 18089, 613, 409, 9419, 193189], start_index=1)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(103)
        q = math.prod(self(k) for k in range(1, n))
        r = q * 17
        val = (pow(r, 17) - 1)//(r - 1)
        for prime_factor in factor.generate_factors_by_size(val):
            if gmpy2.is_congruent(prime_factor, 1, 17):
                return prime_factor


sys.modules[__name__] = A125038()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A125038()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
