import itertools
import sys
import logging

import gmpy2

from oeispy.core import Sequence
from oeispy.utils import factor


class A080670(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        factors = factor.factors_as_dict(n)
        if factors == -1:
            exit(1)
            return -1
        return gmpy2.mpz("".join([str(prime)+(str(exponent) if exponent > 1 else "") for prime, exponent in factors.items()]))


sys.modules[__name__] = A080670()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A080670().enumerate():
        print(f"{n} {val}")
