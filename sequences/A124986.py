import itertools
import logging
import math
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A124986(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[5, 101, 1020101, 53, 29, 2507707213238852620996901, 449, 433361, 401, 925177698346131180901394980203075088053316845914981, 44876921, 17, 173, 55825320961636911896609423781787726742085766063170279232951937797974217605020249600034222953624856258324736856981851815668295021896581657855545778651849954285130423890244658579145089221903909], start_index=1)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(5)
        q = math.prod(self(k) for k in range(1, n))
        val = 4 * pow(q, 2) + 1
        for prime_factor in factor.generate_factors_by_size(val):
            if gmpy2.is_congruent(prime_factor, 5, 13):
                return prime_factor


sys.modules[__name__] = A124986()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A124986()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
