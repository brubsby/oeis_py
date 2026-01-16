import itertools
import logging
import math
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A124989(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[19, 7219, 462739, 509, 129229, 295380580489, 9653956849, 149, 110212292237172705230749846071050188009093377022084806290042881946231583507557298889, 157881589, 60397967745386189, 1429, 79, 4782452785522769532192881861627261788045468028263505258140488520485380057034658537066501492677804226040664472729296708469109781878934667345750484101889534495867391419508269120973815250313475977114982776015479469844704744259909177940868791248608372913274698453660049245658376142419], start_index=1)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(19)
        q = math.prod(self(k) for k in range(1, n))
        val = 100 * pow(q, 2) - 5
        for prime_factor in factor.generate_factors_by_size(val):
            if gmpy2.is_congruent(prime_factor, 9, 10):
                return prime_factor


sys.modules[__name__] = A124989()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A124989()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
