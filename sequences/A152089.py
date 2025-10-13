import itertools
import logging
import sys
import gmpy2
import math

from modules import factor, base, prime, semiprime, factordb
from sequence import Sequence


class A152089(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self(n-1)+1 if n > 1 else 1
        for k in itertools.count(start=k):
            val = 4 * gmpy2.fac(k) + 1
            primes, composites = factor.factordb_get_known_factorization(val)
            for p, i in primes.items():
                if gmpy2.is_congruent(p, 3, 4):
                    if not gmpy2.is_even(i):
                        return k
            remaining_composite = math.prod([pow(c, i) for c, i in composites.items()])
            primes = factor.factors_as_dict(remaining_composite, check_factor_db=False)
            for p, i in primes.items():
                if gmpy2.is_congruent(p, 3, 4):
                    if not gmpy2.is_even(i):
                        return k



sys.modules[__name__] = A152089()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A152089()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
