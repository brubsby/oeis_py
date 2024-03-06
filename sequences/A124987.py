import itertools
import logging
import math
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A124987(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[5, 29, 17, 6076229, 1289, 78067083126343039013, 521, 8606045503613, 15837917, 1873731749, 809, 137, 2237, 17729, 698136143002592389753545709194538322666965621767137227728697539791309577726683789106157939645023729461969], start_index=1)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(5)
        q = math.prod(self(k) for k in range(1, n))
        val = pow(q, 2) + 4
        for prime_factor in factor.generate_factors_by_size(val):
            if gmpy2.is_congruent(prime_factor, 5, 12):
                return prime_factor


sys.modules[__name__] = A124987()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A124987()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
