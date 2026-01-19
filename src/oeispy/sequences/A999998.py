import itertools
import logging
import sys

import primesieve
import math
import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence
from oeispy.sequences import A999999


class A999998(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True, b_file_lookup=True)

    def calculate(self, n):
        lookup_set = set()
        for k in itertools.count(8):
            print(k)
            prev = tuple(A999999.list(k-1, start=k-7))
            if prev in lookup_set:
                raise Exception(f"Loop found at {k}, {prev}")
            lookup_set.add(prev)
            val = math.prod(prev) + 1
            kth = A999999(k)
            if not gmpy2.is_divisible(val, kth):
                raise Exception(f"Error found at {k}, {prev} + 1 = {val} is not divisible by {kth}")


sys.modules[__name__] = A999998()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A999998()
    seq.generate_b_file(max_n=None, term_digit_length_limit=None)
    # for n, val in seq.enumerate():
    #     print(f"{val},")
