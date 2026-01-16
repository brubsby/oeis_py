import itertools
import sys
import logging

from oeispy.utils import factor

from oeispy.core import Sequence

import A007908


class A110756(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True, b_file_lookup=True)

    def calculate(self, n):
        return factor.number_of_divisors(A007908(n))


sys.modules[__name__] = A110756()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A110756()
    seq.generate_b_file(term_cpu_time=10)
    for n, val in seq.enumerate():
        print(f"{n} {val}")
